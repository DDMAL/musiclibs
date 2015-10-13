try:
    from misirlou.helpers.loader import ManifestReader
except:
    from loader import ManifestReader

import urllib.request
from urllib.parse import urlparse
import sys

class Validator:

    def __init__(self, remote_url):
        self.url = remote_url

    def fetch(self, url):
        #fetch content at given url
        try:
            wh = urllib.request.urlopen(url)
        except urllib.request.HTTPError:
            pass
        data = wh.read()
        wh.close()
        return (data, wh)

    def do_test(self):
        url = self.url.strip()
        parsed_url = urlparse(url)

        if not parsed_url.scheme.startswith('http'):
            return {'status': 0,
                    'error': 'URLs must use HTTP or HTTPS',
                    'url': url}

        try:
            (data, webhandle) = self.fetch(url)
        except:
            return {'status': 0, 'error': 'Cannot fetch url', 'url': url}

        # First check HTTP level
        ct = webhandle.headers.get('content-type', '')
        cors = webhandle.headers.get('access-control-allow-origin', '')

        warnings = []
        if not ct.startswith('application/json') and not ct.startswith('application/ld+json'):
            # not json
            warnings.append("URL does not have correct content-type header: got \"%s\", expected JSON" % ct)
        if cors != "*":
            warnings.append("URL does not have correct access-control-allow-origin header:"
                            " got \"%s\", expected *" % cors)

        # Now check data
        reader = ManifestReader(data)
        err = None
        try:
            mf = reader.read()
            mf.toJSON()
            # Passed!
            okay = 1
        except Exception as e:
            err = e
            okay = 0

        warnings.extend(reader.get_warnings())
        return {'url': url, 'status': okay, 'warnings': warnings, 'error': str(err)}


def main(argv):
    v = Validator(argv[0])
    data = v.do_test()
    return data

if __name__ == "__main__":
    main(sys.argv[1:])