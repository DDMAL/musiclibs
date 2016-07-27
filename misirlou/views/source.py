from rest_framework import generics

from misirlou.models import Source
from misirlou.serializers import SourceSerializer


class SourceList(generics.ListCreateAPIView):
    queryset = Source.objects.all()
    serializer_class = SourceSerializer
