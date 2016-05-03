from misirlou.tests.mis_test import MisirlouTestSetup
import time


class ManifestViewTestCase(MisirlouTestSetup):

    def test_post(self):
        """Test that posting in returns a url to check status of job."""
        rem_url = "http://localhost:8888/misirlou/tests/manifest.json"
        resp = self.client.post("/manifests/", {'remote_url': rem_url})
        self.assertTrue(bool(resp.data['status']))

    def test_post_with_status(self):
        """Test that a posted import succeeds quickly and correctly."""
        rem_url = "http://localhost:8888/misirlou/tests/manifest.json"
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

        expected = {'total_count': 1,
                    'succeeded_count': 1,
                    'failed': {},
                    'failed_count': 0,
                    'status': 0
                    }
        # Assert succeeded key is there, but don't care about resulting url.
        self.assertTrue(bool(resp2.data['succeeded'][rem_url]))
        del resp2.data['succeeded']
        self.assertDictEqual(resp2.data, expected)