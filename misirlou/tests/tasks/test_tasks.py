from misirlou.tests.mis_test import MisirlouTestSetup
from misirlou.tasks import *
import requests


class CeleryTaskTestCase(MisirlouTestSetup):
    """Run celery tasks as normal functions to test behaviour."""

    def test_import_single_manifest_success(self):
        rem_url = "http://localhost:8888/misirlou/tests/fixtures/manifest.json"
        data = requests.get(rem_url)
        imp_result = import_single_manifest(data.text, rem_url)
        status, imp_id, url, errors, warnings = imp_result
        self.assertTupleEqual((status, errors, sorted(warnings)),
                              (0, [], sorted(["Warning: manifest SHOULD have thumbnail field. @ data['thumbnail']",
                                       "Warning: Unknown key 'see_also' in 'manifest' @ data['see_also']"])))

