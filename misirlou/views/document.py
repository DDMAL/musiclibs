import urllib
import json

from misirlou.models import Document
from misirlou.serializers import DocumentSerializer

from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status


class ManifestImportError(Exception):
    def __init__(self, message, **kwargs):
        self.message = message
        self.data = kwargs

class DocumentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer


class DocumentList(generics.ListCreateAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    def post(self, request, *args, **kwargs):
        remote_url = request.POST.get('remote_url')

        if not remote_url:
            return Response(
                {'error': 'Did not provide remote_url.'},
                status=status.HTTP_400_BAD_REQUEST)
        try:
            self.import_manifest(remote_url)
        except ManifestImportError as e:
            e.data['error'] = e.message
            return Response(e.data, status=status.HTTP_400_BAD_REQUEST)

    def import_manifest(self, remote_url):
        man_request = urllib.request.Request(remote_url)
        man_request.add_header('Accept',
                               'application/json, application/ld+json')
        man_response = urllib.request.urlopen(man_request)
        content_type = man_response.headers.get_content_type()
        if not (content_type == 'application/json'
                or content_type == 'application/ld+json'):
            raise ManifestImportError('Bad content type. Expected JSON, '
                                      'received %s.' % content_type,
                                      content_type=content_type,
                                      remote_url=remote_url)

        data = man_response.read().decode('utf-8')
        manifest = json.loads(data)

        return Response(status=status.HTTP_201_CREATED)
