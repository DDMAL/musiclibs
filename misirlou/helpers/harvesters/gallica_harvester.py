from .search_scraper import SearchScraper
import re
import argparse
import urllib

MANUSCRIPT_URL = "http://gallica.bnf.fr/services/engine/search/sru?operation=searchRetrieve&version=1.2&maximumRecords=50&query=%28gallica%20all%20%22Manuscrits%20musique%22%29%20and%20dc.type%20all%20%22manuscrit%22%20sortby%20dc.date%2Fsort.ascending&filter=provenance%20all%20%22bnf.fr%22&page=1"
SCORE_URL = "http://gallica.bnf.fr/services/engine/search/sru?operation=searchRetrieve&version=1.2&startRecord=0&maximumRecords=50&page=1&query=%28dc.type%20all%20%22partition%22%29&filter=provenance%20all%20%22bnf.fr%22"


class GallicaScraper(SearchScraper):
    def build_url_list(self, resp, resp_json):
        pageinfo = resp_json['SearchResultsPageFragment']['contenu'] \
            ['SearchResultsFragment']['contenu']['NavigationBarSearchResultsFragment'] \
            ['contenu']['PaginationSearchResultsFragment']
        last_page = int(pageinfo['lastPage']['contenu'])  # The last page to worry about
        try:
            maximumRecords = self.get_int_qs(resp.url, "maximumRecords")  # The number of records per page
        except ValueError:
            maximumRecords = 50

        def build_url(page_num, start_record):
            parsed = urllib.parse.urlparse(resp.url)
            parsed_qs = urllib.parse.parse_qs(parsed[4])
            parsed_qs['page'] = [str(page_num)]
            parsed_qs['startRecord'] = [start_record]
            encoded_qs = urllib.parse.urlencode(parsed_qs, doseq=True)
            return urllib.parse.urlunparse((*parsed[:4], encoded_qs, *parsed[5:]))
        return [build_url(x, (x-1)*maximumRecords) for x in range(1, last_page+1)]

    def build_manifest_urls(self, resp, resp_json):
        GALLICA_IIIF = "http://gallica.bnf.fr/iiif/ark:/{}/manifest.json"

        results = resp_json['SearchResultsPageFragment']['contenu'] \
            ['SearchResultsFragment']['contenu']['ResultsFragment']['contenu']

        def parse_gallica_results(results):
            """Generate manifest urls for results"""
            lst = []
            for result in results:
                url = result['title']['url']
                if "ark:" not in url:
                    if "/search/" in url:
                        # If link was to another search, recurse in and grab it's stuff.
                        gs = GallicaScraper()
                        gs.rate_limiter = self.rate_limiter  # share a single rate limiter.
                        gs.scrape(url)
                        lst.extend(gs.results)
                    continue
                identifier = re.findall(r'ark:\/\d+\/[\w\d]+', url)
                if identifier:
                    identifier = identifier[0].strip("ark:/")
                else:
                    continue
                lst.append(GALLICA_IIIF.format(identifier))
                print(GALLICA_IIIF.format(identifier))
            return lst
        return parse_gallica_results(results)


def _main(harvest_url):
    gs = GallicaScraper()
    gs.scrape(harvest_url)

if __name__ == "__main__":
    description = """Get all IIIF manifest URLS from a Gallica search. Results will be printed on the screen,
    so use redirection to save them in the file of your choice."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("url", type=str, nargs=1, help="The url of a search at http://gallica.bnf.fr/")
    args = parser.parse_args()
    url = args.url[0]
    _main(url)
