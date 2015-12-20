from rest_framework import generics
from rest_framework.response import Response
from rest_framework.reverse import reverse

from misirlou.views.search import do_search


class RootView(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        results = {}
        if request.GET.get('q'):
            results['search'] = do_search(request)

        results['routes'] = {
            'manifests': reverse('manifest-list', request=request),
            'search': reverse('search', request=request)
        }
        return Response(results)
