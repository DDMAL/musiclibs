from django.conf import settings
from django.test import Client
import scorched
from rest_framework.test import APITestCase
from django.test import override_settings


@override_settings(SOLR_SERVER=settings.SOLR_TEST)
class MisirlouTestSetup(APITestCase):
    def setUp_misirlou(self):
        self.client = Client()
        self.solr_con = scorched.SolrInterface(settings.SOLR_SERVER)
        self.solr_con.delete_all()