import uuid
import ujson as json

from misirlou.helpers.manifest_utils.errors import ErrorMap
from misirlou.signals import manifest_imported

import scorched
from collections.abc import Iterable
from django.conf import settings
from django.db import models, connection
from django.db.utils import OperationalError
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

    def indexed(self):
        return super().get_queryset().filter(indexed=True)



class Manifest(models.Model):
    """Generic model to backup imported manifests in a database"""
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    remote_url = models.TextField(unique=True)
    manifest_hash = models.CharField(max_length=40, default="")  # An sha1 hash of the manifest.
    indexed = models.BooleanField(default=False)
    objects = ManifestManager()

    label = models.TextField(null=True, blank=True)
    source = models.ForeignKey("misirlou.Source", blank=True, null=True,
                               related_name="manifests", on_delete=models.SET_NULL)

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
        """Compute and return the url for this manifest with this host."""
        from django.core.urlresolvers import reverse
        return reverse('manifest-detail', args=[str(self.id)])

    def get_stored_manifest(self, to_json=True):
        """Retrieve the stored manifest (that with corrections applied) from solr.

        :param to_json: Bool to load the raw text to a dict before returning.
        :return: Either a json text dump of the manifest, or the loaded dict.
        """
        if not self.indexed:
            raise ValueError("Can't get stored manifest from non-indexed manifest. Use Manifest.objects.indexed().")
        solr_con = scorched.SolrInterface(settings.SOLR_SERVER)
        man = solr_con.query(id=str(self.id)).set_requesthandler('/manifest').execute()
        if to_json:
            return json.loads(man.result.docs[0]['manifest'])
        else:
            return man.result.docs[0]['manifest']

    def re_index(self, force=False, **kwargs):
        """Use the remote_url to retrieve a fresh copy (external) of this manifest and index it."""
        from misirlou.tasks import import_single_manifest
        return import_single_manifest(None, self.remote_url, force=force)

    def re_index_from_stored(self, force=True, **kwargs):
        """Use the stored copy of this manifest to index it again (internal)."""
        from misirlou.tasks import import_single_manifest
        man = self.get_stored_manifest(to_json=False)
        return import_single_manifest(man, self.remote_url, force=force)

    def do_tests(self):
        """Run tests on the manifest and save any warnings or error it has."""
        if not self.indexed:
            raise ValueError("Can't test non-indexed manifest. Use Manifest.objects.indexed().")
        from misirlou.helpers.manifest_utils.tester import ManifestTester
        mt = ManifestTester(self.pk)
        mt.validate(save_result=True)

    def reset_validity(self):
        """Reset the validity, errors and warnings to a pre-tested state."""
        self.is_valid = False
        self.last_tested = None
        self._error = 0
        self._warnings = None

    def _update_solr_validation(self):
        """Update only the 'is_valid' key in the solr document representing this manifest."""
        solr_conn = scorched.SolrInterface(settings.SOLR_SERVER)
        solr_conn.add({"id": str(self.id),
                       "is_valid": {"set": self.is_valid}})

    def set_thumbnail(self, index=None):
        """Set the thumbnail to an image from the sequence at given index."""
        man = self.get_stored_manifest()
        solr_conn = scorched.SolrInterface(settings.SOLR_SERVER)

        if index is None:
            index = len(man['sequences'][0])//2
        try:
            thumbnail = man['sequences'][0]['canvases'][index]['images'][0].get("resource")
        except IndexError:
            print("Could not get image at index {} for manifest at {}".format(index, self.remote_url))
            return
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

    def auto_source(self):
        """Determine the source of this manifest and apply save it's relationship."""
        from misirlou.models import Source
        man = self.get_stored_manifest()
        source = Source.get_source(man)
        self.source = source
        self.save()

    def __str__(self):
        return self.remote_url


@receiver(manifest_imported)
def alert_importer(sender, id=None, local_url=None, **kwargs):
    """Do something whenever a manifest is successfully imported from remote.

    Related to issue #98, regarding firing a POST request to Rodan.
    """
    pass


@receiver(post_delete, sender=Manifest)
def solr_delete(sender, instance, **kwargs):
    solr_conn = scorched.SolrInterface(settings.SOLR_SERVER)
    solr_conn.delete_by_ids(str(instance.id))


@receiver(post_save, sender=Manifest)
def test_if_needed(sender, instance, **kwargs):
    from misirlou.tasks import test_manifest
    must_test = False

    if not instance.indexed:
        return

    if instance.last_tested is None:
        must_test = True
    else:
        time_delta = timezone.now() - instance.last_tested
        if time_delta.days >= 7:
            must_test = True
    if must_test:
        test_manifest.apply_async(args=[str(instance.id)], countdown=60)
