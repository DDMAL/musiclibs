import requests
from collections import namedtuple
import re
import argparse
import urllib

MANUSCRIPT_URL = "http://gallica.bnf.fr/services/engine/search/sru?operation=searchRetrieve&version=1.2&maximumRecords=50&query=%28gallica%20all%20%22Manuscrits%20musique%22%29%20and%20dc.type%20all%20%22manuscrit%22%20sortby%20dc.date%2Fsort.ascending&filter=provenance%20all%20%22bnf.fr%22&page=1"
SCORE_URL = "http://gallica.bnf.fr/services/engine/search/sru?operation=searchRetrieve&version=1.2&startRecord=0&maximumRecords=50&page=1&query=%28dc.type%20all%20%22partition%22%29&filter=provenance%20all%20%22bnf.fr%22"
GALLICA_IIIF = "http://gallica.bnf.fr/iiif/ark:/{}/manifest.json"
JSON_HEADERS = {"Accept": "application/json"}

GallicaResult = namedtuple('GallicaResult', ('results', 'next_url', 'last_url'))
FAILED_COUNT = 0
HARVESTED_COUNT = 0


def parse_gallica_response(resp_dict):
    """Pull out result list and next page."""
    if "SearchResultsPageFragment" not in resp_dict.keys():
        raise ValueError("Could not find search key.")
    pageinfo = resp_dict['SearchResultsPageFragment']['contenu']\
        ['SearchResultsFragment']['contenu']['NavigationBarSearchResultsFragment']\
        ['contenu']['PaginationSearchResultsFragment']
    next_url = pageinfo['nextPage']['url']
    last_url = pageinfo['lastPage']['url']
    results = resp_dict['SearchResultsPageFragment']['contenu']\
        ['SearchResultsFragment']['contenu']['ResultsFragment']['contenu']
    return GallicaResult(results, next_url, last_url)


def parse_gallica_results(results):
    """Generate manifest urls for results"""
    lst = []
    for result in results:
        url = result['title']['url']
        if "ark:" not in url:
            if "/search/" in url:
                # If link was to another search, recurse in and grab it's stuff.
                return harvest_search(url)
            else:
                continue
        identifier = re.findall(r'ark:\/\d+\/[\w\d]+', url)
        if identifier:
            identifier = identifier[0].strip("ark:/")
        else:
            continue
        lst.append(GALLICA_IIIF.format(identifier))
        print(GALLICA_IIIF.format(identifier))
    return lst


def get_qs(target_url, field):
    """Utility to parse a query parameter out."""
    parsed = urllib.parse.urlparse(target_url)
    qs = urllib.parse.parse_qs(parsed[4])
    field_val = qs.get(field)
    return field_val


def get_int_qs(target_url, field):
    """Utility to parse a single int out of a query parameter."""
    val = get_qs(target_url, field)
    if val:
        return int(val[0])
    raise ValueError("Parameter '{}' not in url '{}'".format(field, target_url))


def harvest_search(harvest_url):
    global FAILED_COUNT
    global HARVESTED_COUNT

    # Get first page
    resp = requests.get(harvest_url, headers=JSON_HEADERS, timeout=30)
    results, next_url, last_url = parse_gallica_response(resp.json())
    last_page = get_int_qs(last_url, "page")
    next_page = get_int_qs(next_url, "page")
    results = parse_gallica_results(results)

    # Get all intermediate pages
    while next_page <= last_page:
        resp = requests.get(next_url, headers=JSON_HEADERS)
        try:
            res, next_url, last_url = parse_gallica_response(resp.json())
            next_page = get_int_qs(next_url, "page")
        except ValueError as e:
            FAILED_COUNT += 1
            continue
        results.extend(parse_gallica_results(res))
        HARVESTED_COUNT += 1
    return results


def _main(harvest_url):
    harvest_search(harvest_url)

    global HARVESTED_COUNT
    global FAILED_COUNT
    print("Harvested {} pages of results. Failed {} pages.".format(HARVESTED_COUNT, FAILED_COUNT))

if __name__ == "__main__":
    description = """Get all IIIF manifest URLS from a Gallica search. Results will be printed on the screen,
    so use redirection to save them in the file of your choice."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("url", type=str, nargs=1, help="The url of a search at http://gallica.bnf.fr/")
    args = parser.parse_args()
    url = args.url[0]
    _main(url)
