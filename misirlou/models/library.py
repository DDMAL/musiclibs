from django.db import models
import uuid


class Library(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    iiif_hostname = models.TextField()  # The hostname of this library's IIIF docs.
    home_page = models.TextField(null=True, blank=True)  # Link to the homepage of the library
    name = models.TextField(null=True, blank=True)  # Display name of the library.
    # thumbnail?

    class Meta:
        verbose_name_plural = "Libraries"

    def __str__(self):
        return self.name

    def __repr__(self):
        return "Library({})".format(self.iiif_hostname)

    """Process for associating a manifest with a library:

        1. Search manifest for 'attribution', 'library, 'repository', 'provider'
            keys and associate with a library if one of these keys matches the
            'name' field of an existing library and there are no conflicts.
        2. Associate with a library with a matching iiif_hostname.
        3. Create a library with the given iiif_hostname. Leave home_page
            and name fields to be filled out manually.
    """