from urllib import parse

from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework import status
from rest_framework import generics
from django.conf import settings
import scorched

from misirlou.renderers import SinglePageAppRenderer


class SearchView(generics.GenericAPIView):
    renderer_classes = (SinglePageAppRenderer, JSONRenderer,
                        BrowsableAPIRenderer)

    def get(self, request, *args, **kwargs):
        """Return formatted result based on query"""
        if not request.GET.get('q'):
            return Response({'error': 'Did not provide query (q).'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Determine start row based on page number.
        page = request.GET.get('page')
        if page:
            start = ((int(page)-1)*10)
        else:
            start = 0

        solr_conn = scorched.SolrInterface(settings.SOLR_SERVER)
        response = solr_conn.query(request.GET.get('q'))\
            .set_requesthandler('minimal')\
            .paginate(start=start).execute()

        results = format_response(request, response)

        return Response(results, content_type="charset=utf-8")


def format_response(request, scorched_response):
    """Format response dict according to API
    :param request: django request object
    :param scorched_response: Scorched solr response object
    :return: dict with proper nesting and formatting for response
    """
    num_found = scorched_response.result.numFound
    params = scorched_response.params
    hl = scorched_response.highlighting
    q = params['q']
    documents = scorched_response.result.docs
    page = int(request.GET.get('page', 1))
    request_url = request.build_absolute_uri()

    if num_found % 10:
        max_page = (num_found // 10) + 1
    else:
        max_page = (num_found // 10)

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
            'thumbnail': doc.get('thumbnail'),
            'attribution': doc.get('attribution'),
            'hits': []
        }

        # Append highlights.
        highlights = hl.get(id)
        for k,v in highlights.items():
            values = v[0].split('[$M$]', 3)
            hit = {
                'field': k,
                'prefix': values[0],
                'match': values[1],
                'suffix': values[2]
            }
            result['hits'].append(hit)

        results.append(result)

    response = {
        '@id': request_url,
        'num_found': num_found,
        'q': q,
        'next': next_page,
        'prev': prev_page,
        'last': last_page,
        'results': results
    }

    return response
