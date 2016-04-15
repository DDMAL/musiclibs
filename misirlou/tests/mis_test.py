from django.conf import settings
from django.test import Client
import scorched
from rest_framework.test import APITestCase


class MisirlouTestSetup(APITestCase):

    @classmethod
    def setUpClass(cls):
        settings.SOLR_SERVER = settings.SOLR_TEST
        cls.client = Client()
        cls.solr_con = scorched.SolrInterface(settings.SOLR_SERVER)

    @classmethod
    def tearDownClass(cls):
        pass