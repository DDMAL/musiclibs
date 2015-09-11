from django.db import models


class Manifest(models.Model):
    """Generic model to backup imported manifests in a database"""
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    remote_url = models.TextField(default='')

    class Meta:
        ordering = ('created',)