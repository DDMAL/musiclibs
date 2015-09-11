from django.db import models


class Document(models.Model):
    """Generic model to backup imported manifests in a database"""
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=200, blank=True, default='')
    remote_url = models.TextField(default='')

    class Meta:
        ordering = ('created',)