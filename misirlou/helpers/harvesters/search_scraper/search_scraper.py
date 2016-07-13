from concurrent import futures
from threading import Lock
import queue
import time
import requests
import urllib


class RateLimiter:
    def __init__(self, wait_time):
        """Create a RateLimiter

        :param wait_time: How many seconds to wait between hits.
        """
        self.lock = Lock()
        self.wait_time = wait_time
        self.last_hit = time.time()

    def hit(self):
        """Sleep until allowed to hit."""
        with self.lock:
            t_diff = time.time() - self.last_hit
            if t_diff < self.wait_time:
                time.sleep(self.wait_time - t_diff)
            self.last_hit = time.time()


class SearchScraper:
    JSON_HEADERS = {"Accept": "application/json"}
    MAX_WORKERS = 20

    def __init__(self):
        self.rate_limiter = None
        self._start_url = None
        self.url_list = queue.Queue()
        self.results = []

    def _get_single_page(self, url, headers=None):
        """Get page using requests."""
        if headers is None:
            headers = self.JSON_HEADERS
        if self.rate_limiter:
            self.rate_limiter.hit()
        resp = requests.get(url, headers=headers, timeout=30)
        return resp

    def _scrape_page(self, url, headers=None):
        """Single page entry function for threads."""
        resp = self._get_single_page(url, headers=headers)
        resp_json = resp.json()
        return self.build_manifest_urls(resp, resp_json)

    def _get_robots_crawl_delay(self, url):
        """Get the Crawl-delay from robots.txt if it exits"""
        url = urllib.parse.urljoin(url, "/robots.txt")
        resp = self._get_single_page(url, headers={})
        if resp.status_code < 200 or resp.status_code >= 300:
            return 1

        lines = resp.text.split("\n")
        crawl_delay = 1
        for l in lines:
            if l.startswith("Crawl-delay"):
                crawl_delay = int(l.split(":")[-1])
        return crawl_delay

    def _init_rate_limiter(self, force=False):
        """Create a rate limiter for self to use if don't already have one."""
        if force or not self.rate_limiter:
            cd = self._get_robots_crawl_delay(self._start_url)
            self.rate_limiter = RateLimiter(cd)

    def get_qs(self, target_url, field):
        """Utility to parse a query parameter out of a url."""
        parsed = urllib.parse.urlparse(target_url)
        qs = urllib.parse.parse_qs(parsed[4])
        field_val = qs.get(field)
        return field_val

    def get_int_qs(self, target_url, field):
        """Utility to parse a single int query parameter our of a url."""
        val = self.get_qs(target_url, field)
        if val:
            return int(val[0])
        raise ValueError("Parameter '{}' not in url '{}'".format(field, target_url))

    def build_url_list(self, resp, resp_json):
        """Builds a list of urls that need to be fetched.

        This method is responsible for building a list of urls to
        be fetched. It will be passed the first page of results
        from whatever url is passed to scrape(). It must parse
        this response, and return the list of all urls that will
        be scraped.

        This function must be implemented on a per-site basis, as
        each response will be slightly different.
        """
        raise NotImplemented

    def build_manifest_urls(self, resp, resp_json):
        """Using the response from a page, build a list of manifest urls.

        This method is responsible for building a list of manifest urls;
        the result of scraping a single page. It is called on the
        response from every url returned form self.build_url_list().

        This function must be implemented on a per-site basis, as
        each response will be slightly different.
        """
        raise NotImplemented

    def scrape(self, start_url, headers=None):
        """Scrape paginated search results with rate-limited multithreading."""
        self._start_url = start_url
        self._init_rate_limiter()
        resp = self._get_single_page(start_url)
        self.url_list = self.build_url_list(resp, resp.json())
        workers = min(self.MAX_WORKERS, len(self.url_list))
        with futures.ThreadPoolExecutor(workers) as executor:
            results = executor.map(lambda url: self._scrape_page(url, headers=headers), self.url_list)
        for r in results:
            self.results.extend(r)
