from misirlou.helpers.IIIFImporter import WIPManifest
from misirlou.models.manifest import Manifest
from misirlou.tests.mis_test import MisirlouTestSetup
import uuid
import ujson as json
from urllib.request import urlopen


class WIPManifestTestCase(MisirlouTestSetup):
    def setUp(self):
        self.setUp_misirlou()
        self.v_id = str(uuid.uuid4())
        self.v_url = "http://www.e-codices.unifr.ch/metadata/iiif/zhl-0035-4/manifest.json"
        with open("misirlou/tests/manifest.json") as f:
            self.w_valid = WIPManifest(self.v_url, self.v_id, prefetched_data=f.read())

    def test_no_duplicates(self):
        self.w_valid._check_db_duplicates()
        self.assertEqual(self.w_valid.id, self.v_id)

    def test_is_duplicates(self):
        temp_id = str(uuid.uuid4())
        temp = Manifest(remote_url=self.v_url, id=temp_id)
        temp.save()
        self.w_valid._check_db_duplicates()

        # found the duplicate in the database.
        self.assertEqual(self.w_valid.id, temp_id)
        self.w_valid.id = self.v_id
        temp.delete()

    def test_solr_index(self):
        """ Index a known manifest, check that the indexing function
        correctly splits the items into language fields, and
        that the solr_delete function runs smoothly.
        """
        self.w_valid._retrieve_json()
        self.w_valid._solr_index()
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
        self.assertIn("http://www.e-codices.unifr.ch/metadata/iiif/zhl-0035-4/manifest.json", doc['remote_url'])
        self.assertIn("Luzern", doc['location'])
        self.assertIn("Luzern, Zentral- und Hochschulbibliothek, KB 35 4°", doc['label'])

        self.w_valid._solr_delete()
        self.solr_con.commit()
        response = self.solr_con.query(id=self.v_id).execute()
        self.assertEqual(response.result.numFound, 0)

    def test_valid_retrieval(self):
        manifest_resp = urlopen(self.v_url)
        manifest_data = manifest_resp.read().decode('utf-8')
        manifest_json = json.loads(manifest_data)

        self.w_valid._retrieve_json()
        self.assertEqual(manifest_json, self.w_valid.json)

    def test_valid_create(self):
        """Test ability to create a manifest using WIPManifest
        and a manifest that is known to succeed. Verify that this
        adds a document to solr and sql.
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


