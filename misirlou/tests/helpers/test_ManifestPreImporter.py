from misirlou.helpers.manifest_utils.importer import ManifestPreImporter
from misirlou.tests.mis_test import MisirlouTestSetup


class PreImporterTestCase(MisirlouTestSetup):
    def test_get_top_manifest(self):
        """ If there are no nested manifests, simply return the top level url."""
        pre_importer = ManifestPreImporter("http://localhost:8888/misirlou/tests/fixtures/manifest.json")
        url_list = pre_importer.get_all_urls()
        self.assertListEqual(['http://localhost:8888/misirlou/tests/fixtures/manifest.json'], url_list)

    def test_get_embedded_manifest(self):
        """ Get a manifest embedded in a collection. """
        pre_importer = ManifestPreImporter("http://localhost:8888/misirlou/tests/fixtures/collection_bottom.json")
        url_list = pre_importer.get_all_urls()
        self.assertListEqual(['http://localhost:8888/misirlou/tests/fixtures/manifest.json'], url_list)

    def test_get_nested_col(self):
        """ Get only manifest URLs when scarping through nested collections."""
        pre_importer = ManifestPreImporter("http://localhost:8888/misirlou/tests/fixtures/collection_top.json")
        url_list = pre_importer.get_all_urls()
        self.assertListEqual(['http://localhost:8888/misirlou/tests/fixtures/manifest.json'], url_list)
