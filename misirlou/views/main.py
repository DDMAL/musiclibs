from rest_framework import generics
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.reverse import reverse

from misirlou.renderers import SinglePageAppRenderer


class ApiRootView(generics.GenericAPIView):
    renderer_classes = (SinglePageAppRenderer, JSONRenderer,
                        BrowsableAPIRenderer)

    def get(self, request, *args, **kwargs):
        return Response({
            'manifests': reverse('manifest-list', request=request),
            'search': reverse('search', request=request)
        })
