from urllib import parse
import ujson as json
import requests

from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework import generics
from django.conf import settings
from rest_framework.reverse import reverse

from misirlou.renderers import SinglePageAppRenderer
from misirlou.models import Manifest


class RootView(generics.GenericAPIView):
    renderer_classes = (SinglePageAppRenderer, JSONRenderer,
                        BrowsableAPIRenderer)

    def get(self, request, *args, **kwargs):
        results = do_search(request)

        if should_redo_search(results):
            collation = results['spellcheck']['collationQuery']
            results = do_search(request, q=collation)
            results['applied_correction'] = [request.GET.get('q'), collation]

        resp = {
            'routes': {'manifests': reverse('manifest-list', request=request)},
            'search': results
        }
        return Response(resp)


class StatsView(generics.GenericAPIView):
    renderer_classes = (JSONRenderer,)

    def get(self, request, *args, **kwargs):
        """Return basic stats about the indexed data."""
        libraries = Manifest.objects.library_count()
        man_count = Manifest.objects.all().count()

        return Response({"manifests": man_count, "attributions": libraries})


def do_search(request, q=None, m=None):
    q = q if q else request.GET.get('q')
    m = m if m else request.GET.get('m')
    page = request.GET.get('page')
    if page:
        start = ((int(page)-1)*10)
    else:
        start = 0

    if q and m:
        res = do_music_join_search(q, m, start)
    elif m and not q:
        res = do_music_join_search("*:*", m, start)
    elif q and not m:
        res = do_minimal_search(q, start)
    else:
        return None

    return format_response(request, res)


def do_minimal_search(q, start):
    uri = [settings.SOLR_SERVER]
    uri.append('minimal')
    uri.append("?q={}".format(q))
    uri.append("&start={}".format(start))
    uri = "".join(uri)
    res = requests.get(uri)
    return res.json()


def do_music_join_search(q, m, start):
    """Get the documents which contain both the metadata and pitch strings."""

    # Get the metadata of documents which match pitch string query.
    uri = [settings.SOLR_SERVER]
    uri.append('minimal?fq={!join from=document_id to=id fromIndex=%s}pnames:' % settings.SOLR_OCR_CORE)
    uri.append(m)
    uri.append('&q={}'.format(q))
    uri = ''.join(uri)
    resp = requests.get(uri).json()

    # Find up to 4 regions where this pitch string occurs in each doc.
    ids = ",".join([doc['id'] for doc in resp['response']['docs']])
    fq = "{!terms f=document_id}" + ids
    uri = [settings.SOLR_OCR]
    uri.append('regions?q={}&fq={}'.format(m, fq))
    uri.append('&group=on&group.field=document_id&group.sort=pagen asc&group.limit=4')
    uri.append('&start={}'.format(start))
    uri = ''.join(uri)
    ocr_info = requests.get(uri).json()['grouped']['document_id']['groups']
    ocr_info = {doc['groupValue']: add_easy_url(doc['doclist']['docs']) for doc in ocr_info}

    # Combine the results into the scorched response
    for doc in resp['response']['docs']:
        doc['omr_hits'] = ocr_info[doc['id']]

    return resp


def add_easy_url(ocr_info):
    """Add an 'easy' url to look at the region in the ocr info dict."""
    for doc in ocr_info:
        loc = json.loads(doc['location'].replace("'", '"'))
        doc['location'] = loc
        easy_url = []
        for l in loc:
            easy_url.append(doc['image_url'] +\
                            "/{},{},{},{}/full/0/default.jpg".format(l['ulx'], l['uly'], l['width'], l['height']))
        doc['easy_url'] = easy_url
    return ocr_info


def should_redo_search(results):
    """Check if the search can and should be re-done with a collation."""
    if not results:
        return False
    nums = results['num_found']
    spellcheck = results['spellcheck']
    cq = None
    if spellcheck:
        cq = spellcheck.get("collationQuery")
    return bool(nums == 0 and cq)


def format_response(request, json_response, page_by=10):
    """Format response dict according to API
    :param request: django request object
    :param result: JSON result from solr search.
    :return: dict with proper nesting and formatting for response
    """

    num_found = json_response['response']['numFound']
    params = json_response['responseHeader']['params']
    hl = json_response['highlighting']
    q = params['q']
    m = params.get('m')
    documents = json_response['response']['docs']
    page = int(request.GET.get('page', 1))
    request_url = request.build_absolute_uri()

    if num_found % page_by:
        max_page = (num_found // page_by) + 1
    else:
        max_page = (num_found // page_by)

    scheme, netloc, path, query_string, fragment = parse.urlsplit(request_url)
    qs = parse.parse_qs(query_string)

    # Finding next page.
    if page < max_page:
        qs['page'] = page + 1
        query_string = parse.urlencode(qs, doseq=True)
        next_page = parse.urlunsplit((scheme, netloc, path, query_string, fragment))
    else:
        next_page = None

    # Finding previous page.
    if page > 1:
        qs['page'] = page - 1
        query_string = parse.urlencode(qs, doseq=True)
        prev_page = parse.urlunsplit((scheme, netloc, path, query_string, fragment))
    else:
        prev_page = None

    # Finding last page.
    qs['page'] = max_page
    query_string = parse.urlencode(qs, doseq=True)
    last_page = parse.urlunsplit((scheme, netloc, path, query_string, fragment))

    results = []
    for doc in documents:
        id = doc.get('id')
        result = {
            '@id': doc.get('remote_url'),
            'local_id': id,
            'label': doc.get('label'),
            'description': doc.get('description'),
            'attribution': doc.get('attribution'),
            'omr_hits': doc.get('omr_hits'),
            'hits': []
        }

        thumbnail = doc.get('thumbnail')
        result['thumbnail'] = json.loads(thumbnail) if thumbnail else None
        logo = doc.get('logo')
        result['logo'] = json.loads(logo) if logo else None

        # Append highlights.
        highlights = hl.get(id)
        for k, v in highlights.items():
            values = v[0].split('[$M$]')
            hit = {
                'field': k,
                'parsed': [v for v in values]
            }
            result['hits'].append(hit)

        results.append(result)

    response = {
        '@id': request_url,
        'num_found': num_found,
        'q': q,
        'm': m,
        'next': next_page,
        'prev': prev_page,
        'last': last_page,
        'results': results,
        'spellcheck': None
    }

    if json_response.get('spellcheck') and json_response['spellcheck']['collations']:
        response['spellcheck'] = json_response['spellcheck']['collations'][1]

    return response
