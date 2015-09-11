from rest_framework import generics
from rest_framework.response import Response
from rest_framework.reverse import reverse

class ApiRootView(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        return Response({
            'manifests': reverse('manifest-list', request=request),
            'search': reverse('search', request=request)
        })