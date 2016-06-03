import uuid
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_delete


class Manifest(models.Model):
    """Generic model to backup imported manifests in a database"""
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    remote_url = models.TextField(unique=True)
    manifest_hash = models.CharField(max_length=40, default="")  # An sha1 hash of the manifest.

    is_valid = models.BooleanField(default=True)
    error = models.IntegerField(default=0)
    warnings = models.CommaSeparatedIntegerField(null=True, blank=True)

    class Meta:
        ordering = ('-created',)
        app_label = 'misirlou'

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('manifest-detail', args=[str(self.id)])

    def re_index(self, **kwargs):
        from misirlou.helpers.IIIFImporter import WIPManifest
        text_id = str(self.id)
        wip = WIPManifest(self.remote_url, text_id)
        wip.create()

    def __str__(self):
        return self.remote_url

@receiver(post_delete, sender=Manifest)
def solr_delete(sender, instance, **kwargs):
    import scorched
    from django.conf import settings
    solr_conn = scorched.SolrInterface(settings.SOLR_SERVER)
    response = solr_conn.query(id=instance.id).execute()
    if response.result.docs:
        solr_conn.delete_by_ids([x['id'] for x in response.result.docs])
