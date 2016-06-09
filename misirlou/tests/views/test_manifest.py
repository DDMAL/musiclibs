import time
import itertools
import uuid
import ujson as json

from misirlou.tests.mis_test import MisirlouTestSetup
from misirlou.helpers.IIIFImporter import WIPManifest


class ManifestViewTestCase(MisirlouTestSetup):

    def test_post(self):
        """Test that posting in returns a url to check status of job."""
        rem_url = "http://localhost:8888/misirlou/tests/fixtures/manifest.json"
        resp = self.client.post("/manifests/", {'remote_url': rem_url})
        self.assertTrue(bool(resp.data['status']))

    def test_post_with_status(self):
        """Test that a posted import succeeds quickly and correctly."""
        rem_url = "http://localhost:8888/misirlou/tests/fixtures/manifest.json"
        resp = self.client.post("/manifests/", {'remote_url': rem_url})
        self.assertTrue(bool(resp.data['status']))

        resp2 = self.client.get(resp.data['status'])

        # Wait for the celery import to finish while polling.
        time_waited = 0
        while resp2.data['status'] == 1:
            if time_waited >= 5:
                raise TimeoutError("Waited over 5 seconds for celery to import.")
            time.sleep(0.5)
            time_waited += 0.5
            resp2 = self.client.get(resp.data['status'])

        """Assert succeeded key is there, but don't care about resulting url,
        as it will contain a newly generated uuid."""
        self.assertTrue(bool(resp2.data['succeeded'][rem_url]))
        del resp2.data['succeeded']

        expected = {'total_count': 1,
                    'succeeded_count': 1,
                    'failed': {},
                    'failed_count': 0,
                    'status': 0
                    }
        self.assertDictEqual(resp2.data, expected)


class RecentManifestViewTestCase(MisirlouTestSetup):
    def test_get(self):
        # Create and index a manifest.
        v_id = str(uuid.uuid4())
        v_url = "http://localhost:8888/misirlou/tests/fixtures/manifest.json"

        with open("misirlou/tests/fixtures/manifest.json") as f:
            w_valid = WIPManifest(v_url, v_id, prefetched_data=f.read())

        w_valid.create()
        w_valid.db_rep.is_valid = True
        w_valid.db_rep.save()
        w_valid.db_rep._update_solr_validation()
        self.solr_con.commit()

        with open('misirlou/tests/fixtures/recent_manifests.json') as f:
            expected = json.load(f)

        actual = self.client.get('/manifests/recent/').json()

        for result in itertools.chain(expected['results'], actual['results']):
            del result['local_id']

        self.assertDictEqual(actual, expected)
