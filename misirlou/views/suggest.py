from rest_framework import generics
from rest_framework.response import Response
from django.conf import settings
from rest_framework.renderers import JSONRenderer
import requests
import ujson as json


class SuggestView(generics.GenericAPIView):
    renderer_classes = (JSONRenderer,)

    def get(self, request, *args, **kwargs):
        """Return formatted result based on query"""
        q = request.GET.get('q')
        if not q or len(q) < 3:
            return Response({'suggestions': []})

        url = [settings.SOLR_SERVER]
        url.append("suggest/")
        url.append("?q={}".format(q))
        resp = requests.get("".join(url))
        suggestions = json.loads(resp.content)['suggest']['suggest_musiclibs'][q]['suggestions']
        suggestions.sort(key=lambda v: -v['weight'])
        suggestions = [s['term'] for s in suggestions if s['term'] != q]
        return Response({'suggestions': suggestions})
