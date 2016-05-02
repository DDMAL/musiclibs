from misirlou.tests.mis_test import MisirlouTestSetup
import json


class MainViewTestCase(MisirlouTestSetup):

    def test_get_json(self):
        """Test routes on main page work."""
        res = self.client.get("/?format=json")
        expected = {
            "routes": {
                "manifests": "http://testserver/manifests/?format=json",
            }
        }
        self.assertDictEqual(res.data, expected)

    def test_get_200(self):
        """Test getting a 200 code from the main page. """
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)

    def test_search(self):
        res = self.client.get("/?q=test&format=json")
        expected = {
            "search":
                {"results": [],
                 "last": "http://testserver/?format=json&page=0&q=test",
                 "spellcheck": None,
                 "@id": "http://testserver/?format=json&q=test",
                 "q": "test",
                 "num_found": 0,
                 "prev": None,
                 "next": None},
            "routes":
                {"manifests": "http://testserver/manifests/?format=json"}
        }
        res.data['search']['last'] = self.normalize_url(res.data['search']['last'])
        res.data['search']['@id'] = self.normalize_url(res.data['search']['@id'])
        self.assertDictEqual(res.data, expected)
