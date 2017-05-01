import time
import requests
import redis
import redlock
from urllib.parse import urlsplit
from django.conf import settings


class RippingError(Exception):
    pass


def get_crawl_delay(domain):
    """Figure out the lowest crawl delay in the robots.txt of this domain.

    If not present or not found, default to crawl-delay of 1. Max out at
    waiting 30 seconds between gets (we're not *that* nice).
    """
    cd = 1
    resp = requests.get('http://' + domain + '/robots.txt')
    if 300 >= resp.status_code:
        return cd

    min_cd = 30
    found = False
    for line in resp.iter_lines():
        line = line.decode('utf-8')
        if line.startswith('Crawl-delay'):
            try:
                min_cd = min(min_cd, int(line.split(":")[-1]))
                found = True
            except ValueError:
                continue
    if found:
        return min_cd
    return cd


def get_domain(url):
    o = urlsplit(url)
    return o.netloc


class DomainBasedRespectfulRequester:
    """Makes requests while attempting to respect a domains robots.txt"""

    def __init__(self):
        """Create a DomainBasedFuzzingRequester"""
        self._domain_crawl_delay = {}
        self._domain_last_hit_time = {}

    def get(self, url, **kwargs):
        """Make a request with respect to the crawl-delay on a particular domain."""

        # Figure out the crawl delay for this domain, if we don't have it yet.
        domain = get_domain(url)
        if domain not in self._domain_crawl_delay:
            self._domain_crawl_delay[domain] = get_crawl_delay(domain)
        crawl_delay = self._domain_crawl_delay[domain]

        # Wait until next request at this domain is allowed
        if domain in self._domain_last_hit_time:
            last_hit = self._domain_last_hit_time[domain]
            wait_time = last_hit + crawl_delay - time.time()
            if wait_time > 0:
                time.sleep(wait_time)

        self._domain_last_hit_time[domain] = time.time()

        # get the stuff using requests
        resp = requests.get(url, **kwargs)
        return resp


class RedisRespectfulRequester(DomainBasedRespectfulRequester):
    """Uses redis distributed lock to ensure multiprocess respectful requesting."""

    _LOCKED = 1
    _UNLOCKED = 0

    def __init__(self):
        super().__init__()
        self._redis = redis.StrictRedis(host='localhost', port=settings.REDIS_PORT, db=settings.REDIS_SERVER)
        self._redlock = redlock.Redlock([{"host": "localhost", "port": settings.REDIS_PORT, "db": settings.REDIS_SERVER}, ])

    def get(self, url, **kwargs):
        domain = get_domain(url)
        if domain not in self._domain_crawl_delay:
            self._domain_crawl_delay[domain] = get_crawl_delay(domain)
        time_between_requests = self._domain_crawl_delay[domain]
        domain_lock_key = 'musiclibs_RRR_domain_lock_{}'.format(domain)
        domain_next_access_key = 'musiclibs_RRR_domain_next_access{}'.format(domain)

        # Spin until we get a lock on this domain
        lock = False
        while True:
            lock = self._redlock.lock(domain_lock_key, 15000)
            if lock:
                break
            else:
                time.sleep(0.2)

        try:
            # Wait between each request to a domain.
            next_access = self._redis.get(domain_next_access_key)
            next_access = float(next_access) if next_access else 0.0
            curr_time = time.time()
            wait_time = 0
            if next_access and next_access > curr_time:
                wait_time = next_access - curr_time
                time.sleep(wait_time)

            # Set the next access time and unlock the domain.
            self._redis.set(domain_next_access_key, curr_time + wait_time + time_between_requests)
        finally:
            self._redlock.unlock(lock)

        # Get the thing.
        return requests.get(url, **kwargs)

DEFAULT_REQUESTER = RedisRespectfulRequester()
