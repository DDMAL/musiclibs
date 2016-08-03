from rest_framework import serializers
from misirlou.models import Source


class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = ('id', 'iiif_hostname', 'home_page', 'name')
