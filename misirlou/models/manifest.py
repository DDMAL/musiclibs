import uuid
import requests
import ujson as json

from misirlou.helpers.manifest_utils.errors import ErrorMap

import scorched
from collections.abc import Iterable
from django.conf import settings
from django.db import models, connection
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils import timezone

ERROR_MAP = ErrorMap()

class ManifestManager(models.Manager):
    def with_warning(self, warn):
        """Get all manifests with a particular warning."""
        warn = ERROR_MAP[warn]
        reg = r'([^\d]|^){}([^\d]|$)'.format(str(int(warn)))
        return super().get_queryset().filter(_warnings__regex=reg)

    def with_error(self, err):
        """Get all manifests with a particular error."""
        err = ERROR_MAP[err]
        return super().get_queryset().filter(_error=int(err))

    def without_error(self):
        return super().get_queryset().filter(_error=0)

    def library_count(self):
        cursor = connection.cursor()
        cursor.execute("""
          select COUNT(*)
          FROM (select substring(remote_url from '.*://([^/]*)') as hostname
          from misirlou_manifest
          group by hostname) as hostcounts""")
        return cursor.fetchone()[0]

class Manifest(models.Model):
    """Generic model to backup imported manifests in a database"""
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    remote_url = models.TextField(unique=True)
    manifest_hash = models.CharField(max_length=40, default="")  # An sha1 hash of the manifest.
    objects = ManifestManager()

    is_valid = models.BooleanField(default=False)
    last_tested = models.DateTimeField(null=True, blank=True)
    _error = models.IntegerField(default=0)
    _warnings = models.CommaSeparatedIntegerField(null=True, blank=True, max_length=100)

    class Meta:
        ordering = ('-created',)
        app_label = 'misirlou'

    @property
    def error(self):
        if not self._error:
            return None
        return ERROR_MAP[self._error]

    @error.setter
    def error(self, err):
        self._error = int(err)

    @property
    def warnings(self):
        if not self._warnings:
            return []
        return [ERROR_MAP[int(i)] for i in self._warnings.split(',')]

    @warnings.setter
    def warnings(self, iter):
        if not isinstance(iter, Iterable):
            raise ValueError("Warnings must be an iterable of integers.")
        self._warnings = ",".join(str(int(i)) for i in iter)

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('manifest-detail', args=[str(self.id)])

    def re_index(self, **kwargs):
        from misirlou.tasks import import_single_manifest
        return import_single_manifest(None, self.remote_url)

    def do_tests(self):
        from misirlou.helpers.manifest_utils.tester import ManifestTester
        mt = ManifestTester(self.pk)
        mt.validate(save_result=True)

    def _update_solr_validation(self):
        """Change the solr docs validation """
        solr_conn = scorched.SolrInterface(settings.SOLR_SERVER)
        solr_conn.add({"id": str(self.id),
                       "is_valid": {"set": self.is_valid}})

    def set_thumbnail(self, index):
        """Set the thumbnail to an image from the sequence at given index."""
        solr_conn = scorched.SolrInterface(settings.SOLR_SERVER)
        resp = solr_conn.query(str(self.pk)).set_requesthandler("/manifest").execute()
        man = json.loads(resp.result.docs[0]['manifest'])
        thumbnail = man['sequences'][0]['canvases'][index]['images'][0].get("resource")
        solr_conn.add({"id": str(self.id),
                       "thumbnail": {"set": json.dumps(thumbnail)}})

    def modify_solr_property(self, **kwargs):
        """Modify properties of the indexed solr document.

        Any field besides 'id' can be set using kwargs.
        """
        changes = {k: {"set": v} for k, v in kwargs.items()}
        changes["id"] = str(self.id)
        solr_conn = scorched.SolrInterface(settings.SOLR_SERVER)
        solr_conn.add(changes)

    def __str__(self):
        return self.remote_url


@receiver(post_delete, sender=Manifest)
def solr_delete(sender, instance, **kwargs):
    solr_conn = scorched.SolrInterface(settings.SOLR_SERVER)
    solr_conn.delete_by_ids(str(instance.id))


@receiver(post_save, sender=Manifest)
def test_if_needed(sender, instance, **kwargs):
    from misirlou.tasks import test_manifest
    must_test = False
    if instance.last_tested is None:
        must_test = True
    else:
        time_delta = timezone.now() - instance.last_tested
        if time_delta.days >= 1:
            must_test = True
    if must_test:
        test_manifest.apply_async(args=[str(instance.id)], countdown=60)
