from rest_framework import generics
from rest_framework.response import Response
from django.conf import settings
from rest_framework.renderers import JSONRenderer
import requests
import time
import ujson as json
import itertools


class SuggestView(generics.GenericAPIView):
    renderer_classes = (JSONRenderer,)

    def get(self, request, *args, **kwargs):
        """Return formatted result based on query"""

        # Measure turn around time if debug is on.
        if settings.DEBUG:
            start_time = time.time()

        # Get the query, or return a default response if one is not present.
        q = request.GET.get('q')
        if not q or len(q) < 3:
            return Response({'suggestions': []})
        split_q = q.split(" ")
        last_word = split_q[-1]

        # Make the request to the search server.
        url = settings.SOLR_SERVER + "suggest/?q={}".format(q)
        resp = requests.get(url)

        # Parse out phrase and word suggestions and combine them.
        phrase_suggestions = json.loads(resp.content)['suggest']['phrase_suggestions'][q]['suggestions']
        phrase_suggestions = [s['term'] for s in phrase_suggestions]
        word_suggestions = json.loads(resp.content)['suggest']['word_suggestions'][q]['suggestions']
        word_suggestions = [" ".join(itertools.chain(split_q[:-1], [s['term']]))
                            for s in word_suggestions if s['term'] != last_word]
        suggestions = phrase_suggestions + word_suggestions

        response = {'suggestions': suggestions}
        if settings.DEBUG:
            response['time'] = time.time() - start_time
        return Response(response)
