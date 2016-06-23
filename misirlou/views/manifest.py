import uuid
import ujson as json
import scorched
import requests

from rest_framework import generics
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from misirlou.renderers import SinglePageAppRenderer
from misirlou.models import Manifest
from misirlou.serializers import ManifestSerializer
from misirlou.views import format_response
from django.conf import settings
from misirlou.helpers.manifest_utils.importer import ManifestPreImporter
from celery import group
from misirlou.tasks import import_single_manifest

RECENT_MANIFEST_COUNT = 12


class ManifestDetail(generics.GenericAPIView):
    renderer_classes = (SinglePageAppRenderer, JSONRenderer)

    def get(self, request, *args, **kwargs):
        man_pk = self.kwargs['pk']
        solr_conn = scorched.SolrInterface(settings.SOLR_SERVER)
        response = solr_conn.query(man_pk).set_requesthandler('/manifest').execute()
        if response.result.numFound != 1:
            data = {
                "error": "Could not resolve manifest '{}'".format(man_pk),
                "numFound": response.result.numFound}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        data = json.loads(response.result.docs[0]['manifest'])
        return Response(data)


class ManifestDetailSearch(generics.GenericAPIView):
    renderer_classes = (JSONRenderer,)

    def get(self, request, *args, **kwargs):
        """Do a search for the """
        man_pk = self.kwargs['pk']
        music = request.GET.get("m")
        page = request.GET.get('p')

        solr_conn = scorched.SolrInterface(settings.SOLR_OCR)
        response = solr_conn.query(pnames=music, pagen=page).paginate(start=0, rows=100)\
            .filter(document_id=man_pk)\
            .field_limit(("neumes", "intervals", "location", "semitones")).execute()
        locations = []
        for doc in response.result.docs:
            doc['location'] = json.loads(doc['location'].replace("'", '"'))

        return Response((doc for doc in response.result.docs))

class ManifestList(generics.ListCreateAPIView):
    queryset = Manifest.objects.all()
    serializer_class = ManifestSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )

    def post(self, request, *args, **kwargs):
        """Import a manifest at a remote_url."""

        remote_url = request.data.get("remote_url")

        if not remote_url:
            return Response(
                {'error': 'Did not provide remote_url.'},
                status=status.HTTP_400_BAD_REQUEST)

        shared_id = str(uuid.uuid4())
        imp = ManifestPreImporter(remote_url)
        lst = imp.get_all_urls()

        # If there are manifests to import, create a celery group for the task.
        if lst:
            if len(lst) == 1:
                g = group([import_single_manifest.s(imp.text, lst[0])])
            else:
                g = group([import_single_manifest.s(None, url) for url in lst]).skew(start=0, step=0.3)
            task = g.apply_async(task_id=shared_id)
            task.save()
        else:
            if imp.errors:
                return Response({'errors': imp.errors}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'errors': ['Failed to find recognisable IIIF manifest data.']}, status=status.HTTP_400_BAD_REQUEST)

        # Return a URL where the status of the import can be polled.
        status_url = reverse('status', request=request, args=[shared_id])
        return Response({'status': status_url}, status.HTTP_202_ACCEPTED)


class RecentManifestList(generics.GenericAPIView):
    """Return a list of the most recently created manifests"""
    renderer_classes = (JSONRenderer,)

    def get(self, request, *args, **kwargs):
        """Get a random assortment of manifests."""
        ids = Manifest.objects.filter(is_valid=True).values_list('pk', flat=True).order_by('?')[:RECENT_MANIFEST_COUNT]
        ids = ",".join(str(pk) for pk in ids)
        fq = "{!terms f=id}" + ids
        uri = [settings.SOLR_SERVER]
        uri.append("minimal/?q=*:*&rows=12")
        uri.append("&fq={}".format(fq))
        uri = "".join(uri)

        resp = scorched.response.SolrResponse.from_json(requests.get(uri).text)
        resp.result.numFound = Manifest.objects.all().count()
        return Response(format_response(request, resp, page_by=RECENT_MANIFEST_COUNT))


class ManifestUpload(generics.RetrieveAPIView):
    """View for the client-side manifest upload form

    This view is not part of the JSON API; it just exposes an endpoint
    to allow HTML clients to serve a form that posts to /manifests/.
    JSON-based clients can perform that post directly.
    """
    renderer_classes = (SinglePageAppRenderer,)
    template_name = 'single_page_app.html'

    def get(self, request, *args, **kwargs):
        return Response()
