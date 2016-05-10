from misirlou.tests.mis_test import MisirlouTestSetup
from misirlou.helpers.IIIFImporter import WIPManifest

import uuid


class SuggestViewTestCase(MisirlouTestSetup):

    def test_suggestions(self):
        # Create and index a manifest.
        v_id = str(uuid.uuid4())
        v_url = "http://localhost:8888/misirlou/tests/fixtures/manifest.json"
        with open("misirlou/tests/fixtures/manifest.json") as f:
            w_valid = WIPManifest(v_url, v_id, prefetched_data=f.read())
        w_valid.create()
        self.solr_con.commit()

        # Some queries with known responses given our test manifest.
        resp = self.client.get("/suggest/?q=serm")
        expected = {'suggestions': ['sermons', 'sermon']}
        self.assertDictEqual(resp.data, expected)

        resp = self.client.get("/suggest/?q=des")
        expected = {'suggestions': ['destiné']}
        self.assertDictEqual(resp.data, expected)

        # A query which should have no suggestions, as it is a complete word.
        resp = self.client.get("/suggest/?q=dimanches")
        expected = {'suggestions': []}
        self.assertDictEqual(resp.data, expected)

        # Forgetting the query parameter is handled silently.
        resp = self.client.get("/suggest/")
        expected = {'suggestions': []}
        self.assertDictEqual(resp.data, expected)
