"""This module defines special handling for manifests from specific libraries.

All functions should return a ManifestSchema() instance to be used by the
validator.

These functions specify exceptions and corrections to be made during validation
and indexing based on the systematic faults of manifests hosted by specific libraries.
They do this by patching the ManifestSchema and ManifestImporter classes with
overriding behaviour before instantiating these newly patched classes and
returning them.

Functions which return ManifestSchemas should be named get_[netloc]_validator,
where [netloc] is the hostname of the library website. Function which return
ManifestImporters should be named get_[netloc]_importer.

If possible (e.g., if all that is required is adding/removing/modifying the
return value of a particular section), the original function should be called
and changes applied afterwards (see get_harvard_edu_validator()).

The patched function should, if possible, check that the error it is designed
to correct is still present before making modifications. This way, if the
library eventually corrects their manifests, re-importing will not result in
erroneous corrections.

Include a doc string for every over-ridden function explaining its purpose.
"""
from misirlou.helpers.manifest_utils.importer import ManifestImporter
from misirlou.helpers.manifest_utils.schema_validator import ManifestSchema
from voluptuous import Schema, Required, ALLOW_EXTRA, Invalid


def get_harvard_edu_validator():
    # Append a context to the image services.
    class PatchedManifestSchema(ManifestSchema):
        def image_service(self, value):
            """Patch in the missing @context key."""
            val = super().image_service(value)
            if not val.get('@context'):
                val['@context'] = 'http://library.stanford.edu/iiif/image-api/1.1/context.json'
                self.warnings.add("Applied library specific corrections.")
            return val
    return PatchedManifestSchema()


def get_vatlib_it_validator():
    class PatchedManifestSchema(ManifestSchema):
        def __init__(self, strict=False):
            """Allow images to not have the required 'on' key."""
            super().__init__(strict=strict)

            # Remove requirement for "on" key in image resources.
            self._ImageSchema = Schema(
                {
                    "@id": self.http_uri,
                    Required('@type'): "oa:Annotation",
                    Required('motivation'): "sc:painting",
                    Required('resource'): self.image_resource,
                    "on": self.http_uri
                }, extra=ALLOW_EXTRA
            )
        def images_in_canvas(self, value):
            val = super().images_in_canvas(value)
            if any(v.get('on') is None for v in val):
                self.warnings.add("Applied library specific corrections.")
    return PatchedManifestSchema()


def get_stanford_edu_validator():
    class PatchedManifestSchema(ManifestSchema):
        def image_resource(self, value):
            """Allow and correct 'dcterms:Image' in place of 'dctypes:Image'."""
            try:
                val = super().image_service(value)
            except Invalid:
                if value.get('@type') == "dcterms:Image":
                    val = self._ImageResourceSchema(value)
                    val['@type'] = "dctypes:Image"
                    self.warnings.add("Applied library specific corrections.")
                elif value.get('@type') == "oa:Choice":
                        val = self._ImageResourceSchema(value['default'])
                        val['@type'] = "dctypes:Image"
                        self.warnings.add("Applied library specific corrections.")
                else:
                    raise
            return val
    return PatchedManifestSchema()


def get_archivelab_org_validator():
    class PatchedManifestSchema(ManifestSchema):
        def __init__(self, strict=False):
            """Allow and correct 'type' instead of '@type' in images."""
            super().__init__(strict=strict)
            self._ImageSchema = Schema(
                {
                    "@id": self.http_uri,
                    '@type': "oa:Annotation",
                    'type': "oa:Annotation",
                    Required('motivation'): "sc:painting",
                    Required('resource'): self.image_resource,
                    "on": self.http_uri
                }, extra=ALLOW_EXTRA
            )
        def images_in_canvas(self, value):
            """Replace 'type' with '@type' in saved document."""
            val = super().images_in_canvas(value)
            for v in (v for v in val if v.get('type')):
                self.warnings.add("Applied library specific corrections.")
                v['@type'] = v['type']
                del v['type']
            return val
    return PatchedManifestSchema()


def get_gallica_bnf_fr_validator():
    class PatchedManifestSchema(ManifestSchema):
        def __init__(self, strict=False):
            """Allow language key to not appear in some LangVal pairs."""
            super().__init__(strict=strict)
            self._LangValPairs = Schema(
                {
                    '@language': self.repeatable_string,
                    Required('@value'): self.repeatable_string
                }
            )

        def metadata_type(self, value):
            """Correct any metadata entries missing a language key in lang-val pairs."""
            values = super().metadata_type(value)
            for value in values:
                v = value.get('value')
                if isinstance(v, list) and not all(vsub.get("@language") for vsub in v):
                    value['value'] = "; ".join((vsub.get("@value") for vsub in v))
            return values

    return PatchedManifestSchema()


def get_gallica_bnf_fr_importer():
    class PatchedManifestImporter(ManifestImporter):
        def _default_thumbnail_finder(self, force_IIIF=True):
            """The gallica thumbnails suck, so force it to pull out image."""
            return super()._default_thumbnail_finder(force_IIIF=True)
    return PatchedManifestImporter
