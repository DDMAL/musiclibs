# -*- coding: utf-8 -*-
from misirlou.tests.mis_test import MisirlouTestSetup
from misirlou.helpers.manifest_utils.importer import ManifestImporter
import uuid


class MainViewTestCase(MisirlouTestSetup):

    def test_get_json(self):
        """Test routes on main page work."""
        res = self.client.get("/?format=json")
        expected = {
            "routes": {
                "manifests": "http://testserver/manifests/?format=json",
            },
            "search": None
        }
        self.assertDictEqual(res.data, expected)

    def test_get_200(self):
        """Test getting a 200 code from the main page. """
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)

    def test_empty_search(self):
        res = self.client.get("/?q=test&format=json")
        expected = {
            "search":
                {"results": [],
                 "last": "http://testserver/?format=json&page=0&q=test",
                 "spellcheck": None,
                 "@id": "http://testserver/?format=json&q=test",
                 "q": "test",
                 "m": None,
                 "num_found": 0,
                 "prev": None,
                 "next": None},
            "routes":
                {"manifests": "http://testserver/manifests/?format=json"}
        }
        res.data['search']['last'] = self.normalize_url(res.data['search']['last'])
        res.data['search']['@id'] = self.normalize_url(res.data['search']['@id'])
        self.assertDictEqual(res.data, expected)

    def test_results_search(self):

        # Create and index a manifest.
        v_id = str(uuid.uuid4())
        v_url = "http://localhost:8888/misirlou/tests/fixtures/manifest.json"
        with open("misirlou/tests/fixtures/manifest.json") as f:
            w_valid = ManifestImporter(v_url, v_id, prefetched_data=f.read())
        w_valid.create()
        self.solr_con.commit()

        res = self.client.get("/?q=Maria&format=json")
        search_data = res.data['search']
        self.assertEqual(search_data['num_found'], 1)
        self.assertEqual(search_data['results'][0]['label'], 'Luzern, Zentral- und Hochschulbibliothek, KB 35 4°')
        expected = {
            'search': {
                'last': 'http://testserver/?format=json&q=Maria&page=1',
                'next': None,
                'spellcheck': None,
                'prev': None,
                'q': 'Maria',
                '@id': 'http://testserver/?q=Maria&format=json',
                'results': [{
                    'label': ['Luzern, Zentral- und Hochschulbibliothek, KB 35 4°'],
                    'logo': None,
                    'description': ['In addition to sermons and sermon-related material pertaining to Sundays, saints’ days and feast-days dedicated to Mary, the manuscript contains part of S. Bonaventure’s (1221-1274) commentary on the four books of the Sentences of Peter Lombard, and the treatise De arca Noe by Marquard of Lindau (d. 1392). '],
                    'thumbnail': {
                        'height': 6496,
                        'format': 'image/jpeg',
                        '@type': 'dctypes:Image',
                        'width': 4872,
                        'service': {
                            'profile': 'http://library.stanford.edu/iiif/image-api/compliance.html#level1',
                            '@context': 'http://iiif.io/api/image/2/context.json',
                            '@id': 'http://www.e-codices.unifr.ch/loris/zhl/zhl-0035-4/zhl-0035-4_e001.jp2'},
                        '@id': 'http://www.e-codices.unifr.ch/loris/zhl/zhl-0035-4/zhl-0035-4_e001.jp2/full/full/0/default.jpg'},
                    'local_id': '183072c6-2eba-4faf-af1c-87f77b7aa229',
                    'hits': [{
                        'field': 'description_txt_it',
                        'parsed': [' dedicate a ', 'Maria', ', il manoscritto contiene parti del commento di s. Bonaventura (1221-1274) al libro']}],
                    '@id': 'http://localhost:8888/misirlou/tests/fixtures/manifest.json',
                    'attribution': ['e-codices - Virtual Manuscript Library of Switzerland']}],
                'num_found': 1},
            'routes': {
                'manifests': 'http://testserver/manifests/?format=json'}}
        self.solr_con.delete_all()
        self.solr_con.commit()

