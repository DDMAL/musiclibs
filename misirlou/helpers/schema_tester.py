import requests
import json
import sys
from voluptuous import MultipleInvalid
from IIIFSchema import ManifestSchema



test = [
    'http://iiif.io/api/presentation/2.0/example/fixtures/1/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/2/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/3/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/4/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/5/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/6/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/7/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/8/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/9/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/10/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/11/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/12/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/13/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/14/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/15/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/16/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/17/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/18/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/19/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/20/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/21/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/22/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/23/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/24/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/25/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/26/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/27/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/28/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/29/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/30/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/31/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/32/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/33/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/34/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/35/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/36/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/37/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/38/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/39/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/40/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/41/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/43/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/44/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/45/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/46/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/47/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/48/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/51/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/52/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/54/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/61/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/62/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/63/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/64/manifest.json',
    'http://iiif.io/api/presentation/2.0/example/fixtures/65/manifest.json']


def interactive():
    """Start a loop to accept URI's from the command line
    and run them against the ManifestSchema."""
    while True:
        uri = input("> ")
        res = requests.get(uri)
        jdump = json.loads(res.text)
        ManifestSchema(jdump)


def automatic():
    """Run against the IIIF edge cases"""
    for item in test:
        res = requests.get(item)
        jdump = json.loads(res.text)
        try:
            ManifestSchema(jdump)
        except MultipleInvalid as e:
            print(item + " failes with error: {}".format(e))

if __name__ == '__main__':
    if sys.argv[-1] == '-i':
        interactive()
    else:
        automatic()

