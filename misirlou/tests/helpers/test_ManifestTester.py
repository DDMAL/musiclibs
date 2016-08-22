import uuid

from misirlou.helpers.manifest_utils.tester import ManifestTester, ManifestTesterException
from misirlou.tasks import import_single_manifest
from misirlou.tests.mis_test import MisirlouTestSetup
from misirlou.models import Manifest


class ErrorMapTestCase(MisirlouTestSetup):

    def import_manifest(self):
        for m in Manifest.objects.all():
            m.delete()
        import_single_manifest(None, 'http://localhost:8888/misirlou/tests/fixtures/manifest.json')
        self.solr_con.commit()

    def create_tester(self):
        self.import_manifest()
        return ManifestTester(Manifest.objects.first().pk)

    def test_retrieve_stored_manifest(self):
        mt = self.create_tester()
        mt._retrieve_stored_manifest()
        self.assertEqual(mt.error, None)

    def test_retrieve_stored_manifest_no_db_record(self):
        with self.assertRaises(ManifestTesterException):
            mt = ManifestTester(uuid.uuid4())
            mt._retrieve_stored_manifest()

    def test_validate(self):
        mt = self.create_tester()
        mt.validate()
        self.assertTrue(mt.is_valid)

