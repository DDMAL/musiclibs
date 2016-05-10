import uuid
import ujson as json
import scorched

from rest_framework import generics
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.reverse import reverse

from misirlou.renderers import SinglePageAppRenderer
from misirlou.models import Manifest
from misirlou.serializers import ManifestSerializer
from django.conf import settings
from misirlou.helpers.IIIFImporter import ManifestPreImporter
from celery import group
from misirlou.tasks import get_document, import_single_manifest


RECENT_MANIFEST_COUNT = 12


class ManifestDetail(generics.GenericAPIView):
    renderer_classes = (SinglePageAppRenderer, JSONRenderer)

    def get(self, request, *args, **kwargs):
        man_pk = self.kwargs['pk']
        solr_conn = scorched.SolrInterface(settings.SOLR_SERVER)
        response = solr_conn.query(man_pk).set_requesthandler('manifest').execute()
        if response.result.numFound != 1:
            data = {
                "error": "Could not resolve manifest '{}'".format(man_pk),
                "numFound": response.result.numFound}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        data = json.loads(response.result.docs[0]['manifest'])
        return Response(data)


class ManifestList(generics.ListCreateAPIView):
    queryset = Manifest.objects.all()
    serializer_class = ManifestSerializer

    def post(self, request, *args, **kwargs):
        """Import a manifest at a remote_url."""
        if request.META.get('CONTENT_TYPE') != 'application/json':
            remote_url = request.POST.get('remote_url')
        else:
            encoding = request.encoding or settings.DEFAULT_CHARSET
            j_dump = json.loads(request.body.decode(encoding))

            if isinstance(j_dump, dict):
                remote_url = j_dump.get('remote_url')
            else:
                remote_url = None

        if not remote_url:
            return Response(
                {'error': 'Did not provide remote_url.'},
                status=status.HTTP_400_BAD_REQUEST)

        shared_id = str(uuid.uuid4())
        imp = ManifestPreImporter(remote_url)
        lst = imp.get_all_urls()

        # If there are manifests to import, create a celery group for the task.
        if lst:
            g = group([get_document.s(url) | import_single_manifest.s(url) for url in lst]).skew(start=0, step=0.3)
            task = g.apply_async(task_id=shared_id)
            task.save()
        else:
            return Response({'error': 'Could not find manifests.', 'status': settings.ERROR})

        # Return a URL where the status of the import can be polled.
        status_url = reverse('status', request=request, args=[shared_id])
        return Response({'status': status_url}, status.HTTP_202_ACCEPTED)


class RecentManifestList(generics.ListAPIView):
    """Return a list of the most recently created manifests"""
    queryset = Manifest.objects.order_by('-created')[:RECENT_MANIFEST_COUNT]
    serializer_class = ManifestSerializer


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
