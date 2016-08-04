from django.db import models
import uuid
import urllib.parse

from misirlou.helpers.json_utils import get_metadata_value, parse_lang_value


class Source(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    iiif_hostname = models.TextField()  # The hostname of this library's IIIF docs.
    home_page = models.TextField(null=True, blank=True)  # Link to the homepage of the library
    name = models.TextField(null=True, blank=True)  # Display name of the library.
    # thumbnail?

    class Meta:
        verbose_name_plural = "Sources"

    def __str__(self):
        return self.name if self.name else self.iiif_hostname

    def __repr__(self):
        return "Source({})".format(self.iiif_hostname)

    @staticmethod
    def get_source(manifest):
        """Find or create a source for a given manifest."""
        attribution = parse_lang_value(manifest.get("attribution"))
        possible_libraries = [attribution]

        lib_keys = ("library", "repository", "provider")
        metadata = manifest.get('metadata')
        for key in lib_keys:
            value = get_metadata_value(metadata, key)
            value = parse_lang_value(value)
            if value:
                possible_libraries.append(value)

        # Return first library that matches one of the collected keys.
        for pl in filter(None, possible_libraries):
            source = Source.objects.filter(name=pl)
            if source:
                return source[0]

        # Return first library with matching hostname in url.
        parsed = urllib.parse.urlparse(manifest.get("@id"))
        source = Source.objects.filter(iiif_hostname=parsed.netloc)
        if source:
            return source[0]
        else:
            # Create a basic library for it to attach to.
            source = Source(iiif_hostname=parsed.netloc, name=attribution)
            source.save()
            return source

    """Process for associating a manifest with a source:

        1. Search manifest for 'attribution', 'library, 'repository', 'provider'
            keys and associate with a source if one of these keys matches the
            'name' field of an existing library and there are no conflicts.
        2. Associate with a source with a matching iiif_hostname.
        3. Create a source with the given iiif_hostname. Leave home_page
            and name fields to be filled out manually.
    """
