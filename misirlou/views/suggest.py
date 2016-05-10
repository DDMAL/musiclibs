from rest_framework import generics
from rest_framework.response import Response
from django.conf import settings
from rest_framework.renderers import JSONRenderer
import scorched


class SuggestView(generics.GenericAPIView):
    renderer_classes = (JSONRenderer,)

    def get(self, request, *args, **kwargs):
        """Return formatted result based on query"""
        q = request.GET.get('q')
        if not q:
            return Response({'suggestions': []})

        solr_conn = scorched.SolrInterface(settings.SOLR_SERVER)
        response = solr_conn.query(q) \
            .set_requesthandler('/suggest').execute()

        suggestions = response.spellcheck['suggestions']
        nice_list = []
        if suggestions:
            nice_list = suggestions[1]['suggestion']
        return Response({'suggestions': nice_list})
