from misirlou.helpers.manifest_utils.importer import ManifestImporter
from misirlou.models.manifest import Manifest
from misirlou.tests.mis_test import MisirlouTestSetup
import uuid
import ujson as json
from urllib.request import urlopen


class ManifestImporterTestCase(MisirlouTestSetup):
    def setUp(self):
        self.v_id = str(uuid.uuid4())
        self.v_url = "http://localhost:8888/misirlou/tests/fixtures/manifest.json"
        with open("misirlou/tests/fixtures/manifest.json") as f:
            self.w_valid = ManifestImporter(self.v_url, self.v_id, prefetched_data=f.read())

    def test_no_duplicates(self):
        """The duplicate checker will do nothing when no duplicates exist."""
        self.w_valid._remove_db_duplicates()
        self.assertEqual(self.w_valid.id, self.v_id)

    def test_is_duplicates(self):
        """Test the duplicate finder is working.

        Ensure that, while creating manifest X, if manifest Y exists
        already and is exactly the same as X, then X will get the same id
        as Y (leading to an over-write, rather than a duplication).
        """
        temp_id = str(uuid.uuid4())
        ManifestImporter(remote_url=self.v_url, shared_id=temp_id).create()
        self.w_valid._remove_db_duplicates()

        # found the duplicate in the database.
        self.assertEqual(self.w_valid.id, temp_id)
        self.w_valid.id = self.v_id

    def test_solr_index(self):
        """Check for correct indexing behaviour.

        Index a known manifest, check that the indexing function correctly
        splits the items into language fields, and that the solr_delete
        function runs smoothly.
        """
        self.w_valid.create()
        self.solr_con.commit()
        response = self.solr_con.query(id=self.v_id).execute()

        self.assertEqual(response.result.numFound, 1)
        doc = response.result.docs[0]
        self.assertIn("In addition to sermons and sermon-related material pertaining to Sundays, saints’ days and feast-days dedicated to Mary, the manuscript contains part of S. Bonaventure’s (1221-1274) commentary on the four books of the Sentences of Peter Lombard, and the treatise De arca Noe by Marquard of Lindau (d. 1392). ", doc['description'])
        self.assertIn("e-codices - Virtual Manuscript Library of Switzerland", doc['attribution'])
        self.assertIn("1453-1454", doc['date'])
        self.assertIn("In addition to sermons and sermon-related material pertaining to Sundays, saints’ days and feast-days dedicated to Mary, the manuscript contains part of S. Bonaventure’s (1221-1274) commentary on the four books of the Sentences of Peter Lombard, and the treatise De arca Noe by Marquard of Lindau (d. 1392). ", doc['description_txt_en'])
        self.assertIn("Neben Predigten und Predigtmaterialien zu Sonntagen, Heiligen- und Marienfesten enthält die Handschrift Teile des Kommentars des hl. Bonaventura (1221-1274) zu den Sentenzenbüchern des Petrus Lombardus sowie den Traktat über die Arche Noah von Marquard von Lindau (gest. 1392). ", doc['description_txt_de'])
        self.assertIn("En plus des sermons et de matériel destiné aux sermons des dimanches, des fêtes mariales et des fêtes de saints, le manuscrit contient des parties du commentaire de saint Bonaventure (1221-1274) sur les Livres des sentences de Pierre Lombard ainsi qu’un traité De arca Noe (sur l’Arche de Noé) de Marquard de Lindau (mort en 1392). ", doc['description_txt_fr'])
        self.assertIn("Oltre a prediche e materiale relativo alle prediche per le domeniche, le feste dei santi e le feste dedicate a Maria, il manoscritto contiene parti del commento di s. Bonaventura (1221-1274) al libro delle sentenze di Pietro Lombardo, ed il trattato De arca Noe di Marquard di Lindau (morto nel 1392). ", doc['description_txt_it'])
        self.assertIn("http://localhost:8888/misirlou/tests/fixtures/manifest.json", doc['remote_url'])
        self.assertIn("Luzern", doc['location'])
        self.assertIn("Luzern, Zentral- und Hochschulbibliothek, KB 35 4°", doc['label'])

        self.w_valid._solr_delete()
        self.solr_con.commit()
        response = self.solr_con.query(id=self.v_id).execute()
        self.assertEqual(response.result.numFound, 0)

    def test_valid_retrieval(self):
        """Ensure getting a manifest remotely works as expected."""
        manifest_resp = urlopen(self.v_url)
        manifest_data = manifest_resp.read().decode('utf-8')
        manifest_json = json.loads(manifest_data)

        self.w_valid._retrieve_json()
        self.assertEqual(manifest_json, self.w_valid.json)

    def test_valid_create(self):
        """Test ability to create a manifest using ManifestImporter.

        Verify that this adds a document to solr and sql.
        """
        self.w_valid.create()
        temp = Manifest.objects.filter(remote_url=self.v_url)
        self.assertEqual(temp.count(), 1)
        self.solr_con.commit()
        response = self.solr_con.query(id=self.v_id).execute()
        doc = temp[0]
        self.assertEqual(str(doc.id), self.v_id)
        self.assertEqual(response.result.numFound, 1)
        doc.delete()
        self.solr_con.commit()
        response = self.solr_con.query(id=self.v_id).execute()
        self.assertEqual(response.result.numFound, 0)

    def test_add_metadata_unknown_keys(self):
        """Test parsing metadata with unknown keys.

        To parse metadata where the key is unknown (not a key indexed in
        solr), the parser should add all the values of the metadata to
        a key called 'metadata' in the solr document. It should also
        preserve language data, if present.
        """
        metadata = {
            "single-unknown": "one",
            "multiple-unknown": ["one", "two"],
            "multiple-unknown-langs": [{'@language': "en", "@value": "one"},
                                        {'@language': "fr", "@value": "deux"}],
            'multiple-unknown-no-en': [{'@language': "de", "@value": "eins"},
                                       {'@language': "it", "@value": "dos"}],
        }
        self.w_valid.doc = {'metadata': []}
        for k, v in metadata.items():
            self.w_valid._add_metadata(k, v)

        #  Needed as hashed keys may appear in any order.
        self.w_valid.doc['metadata'] = sorted(self.w_valid.doc['metadata'])

        correct = {'metadata': ['one', 'one two'],
                   'metadata_txt_de': ['eins'],
                   'metadata_txt_fr': ['deux'],
                   'metadata_txt_en': ['one'],
                   'metadata_txt_it': ['dos']}
        self.assertDictEqual(self.w_valid.doc, correct)

    def test_add_metadata_known_keys(self):
        """Test parsing metadata with known keys.

        When keys are known, the parser should add them as independent keys
        in the document, preserve language data, and set defaults when
        English values are found.
        """

        metadata = {
            'title': "The title",
            'author': [{'@language': "en", "@value": "The Author"},
                       {'@language': "fr", "@value": "Le Author"}],
            'location': [{'@language': 'fr', "@value": "Le Monde"}],
            'period': "Around 14th Century"
        }
        self.w_valid.doc = {'metadata': []}
        for k, v in metadata.items():
            self.w_valid._add_metadata(k, v)

        correct = {'title': 'The title',
                   'author': 'The Author',
                   'author_txt_fr': 'Le Author',
                   'location_txt_fr': 'Le Monde',
                   'date': 'Around 14th Century',
                   'metadata': []}

        self.assertDictEqual(self.w_valid.doc, correct)

    def test_label_normalizer(self):
        """Test behaviour of label normalizer (choosing a label).

        Label normalizer will compare labels against the map defined in
        setings.py. The goal is to match similar words to one indexed field
        (e.g. 'period' -> 'date', 'Title(s)' -> 'title'"

        It should follow this priority in choosing a label

            1) An english label that can be normalized
            2) Any label that can be normalized
            3) Return None (as signifier of no good choices)
        """

        # An english, normalizable label gets priority.
        eng_priority = [{"@language": "fr", "@value": "date"},
                        {"@language": "en", "@value": "title(s)"}]
        l = self.w_valid._meta_label_normalizer(eng_priority)
        self.assertEqual(l, "title")

        # A normalizable label get's priority over an unknown english label.
        norm_priority = [{"@language": "fr", "@value": "publication date"},
                        {"@language": "en", "@value": "Unknown"}]
        l = self.w_valid._meta_label_normalizer(norm_priority)
        self.assertEqual(l, 'date')

        # With no normalization possible, return None.
        no_eng = [{"@language": "fr", "@value": "je ne sais pas"},
                 {"@language": "it", "@value": "unknown"}]
        l = self.w_valid._meta_label_normalizer(no_eng)
        self.assertEqual(l, None)

        # If label is a normalizable string, get it's normalization
        str_test = "publication date"
        l = self.w_valid._meta_label_normalizer(str_test)
        self.assertEqual(l, "date")

        # If label is unknown string, return nothing.
        str_test = "Unknown"
        l = self.w_valid._meta_label_normalizer(str_test)
        self.assertEqual(l, None)

        # Lack of a label returns None
        l = self.w_valid._meta_label_normalizer(None)
        self.assertEqual(l, None)

    def test_file_retrieval(self):
        """Test full creation from local manifest doc."""
        w = ManifestImporter("http://localhost:8888/misirlou/tests/fixtures/manifest.json",
                    str(uuid.uuid4()))
        w.create()
        self.assertDictEqual(self.w_valid.json, w.json)
