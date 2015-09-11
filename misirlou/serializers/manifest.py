from rest_framework import serializers
from misirlou.models import Manifest


class ManifestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manifest
        fields = ('id', 'remote_url')