import uuid
from django.db import models


class Manifest(models.Model):
    """Generic model to backup imported manifests in a database"""
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    indexed = models.BooleanField(default=False)
    errors = models.CharField(max_length=200, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    remote_url = models.TextField(default='')

    class Meta:
        ordering = ('created',)
        app_label = 'misirlou'

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('manifest-detail', args=[str(self.uuid)])
