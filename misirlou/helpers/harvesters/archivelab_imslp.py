import argparse
import urllib.parse
import re
import math

from bs4 import BeautifulSoup
import requests

from search_scraper import SearchScraper


class ArchiveScraper(SearchScraper):
    def build_url_list(self, resp, resp_json=None):
        """The page says there are 26 679 results, but they stop
        as page 133."""

        lst = []
        parsed = urllib.parse.urlparse(resp.url)
        parsed_qs = urllib.parse.parse_qs(parsed.query)
        for i in range(1, 134):
            parsed_qs['page'] = [i]
            encoded_qs = urllib.parse.urlencode(parsed_qs, doseq=True)
            new_parsed = *parsed[:4], encoded_qs, *parsed[5:]
            unparsed = urllib.parse.urlunparse(new_parsed)
            lst.append(unparsed)
        return lst

    def build_manifest_urls(self, resp, resp_json=None):
        soup = BeautifulSoup(resp.text, 'html.parser')
        results = soup.find_all('div', {'class', 'item-ttl'})
        links = []
        for res in results:
            ident = res.a['href'].split('/')[-1]
            link = "https://iiif.archivelab.org/iiif/{}/manifest.json".format(ident)
            links.append(link)
            print(link)
        return links


def _main(harvest_url):
    gs = ArchiveScraper()
    gs.scrape(harvest_url)

if __name__ == "__main__":
    description = """Get all IIIF manifest URLS from a Archive.org collection. Results will be printed on the screen,
    so use redirection to save them in the file of your choice."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("url", type=str, nargs=1, help="The url of a search at http://archive.org")
    args = parser.parse_args()
    url = args.url[0]
    _main(url)
