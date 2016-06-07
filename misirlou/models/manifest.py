import uuid
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_delete
from collections.abc import Iterable
from misirlou.helpers.manifest_errors import ErrorMap
from django.utils import timezone
import scorched
from django.conf import settings


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
        from misirlou.helpers.manifest_tester import ManifestTester
        mt = ManifestTester(self.pk)
        mt.validate(save_result=True)
        self._update_solr_validation()

    def _update_solr_validation(self):
        """Change the solr docs validation """
        solr_conn = scorched.SolrInterface(settings.SOLR_SERVER)
        resp = solr_conn.query(id=str(self.id)).execute()
        if resp.result.numFound != 1:
            self.is_valid = False
            self.error = ERROR_MAP["SOLR_RECORD_ERROR"]
            return
        doc = resp.result.docs[0]
        del doc['manifest_signature']
        del doc['remote_url_signature']
        del doc['_version_']
        doc["is_valid"] = self.is_valid
        solr_conn.add(doc)

    def __str__(self):
        return self.remote_url

@receiver(post_delete, sender=Manifest)
def solr_delete(sender, instance, **kwargs):
    solr_conn = scorched.SolrInterface(settings.SOLR_SERVER)
    solr_conn.delete_by_ids(str(instance.id))