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
    class PatchedManifestSchema(FlexibleManifestSchema):
        def image_service(self, value):
            """Patch in the missing @context key."""
            val = super().image_service(value)
            if not val.get('@context'):
                val['@context'] = 'http://library.stanford.edu/iiif/image-api/1.1/context.json'
                self.warnings.add("Applied library specific corrections.")
            return val

        def image_resource(self, value):
            """Validate image resources inside images list of Canvas"""
            if value.get('@type') in "dctypes:Image":
                return self._ImageResourceSchema(value)
            if value.get('@type') == "dcterms:Image":
                value['@type'] = 'dctypes:Image'
                return self._ImageResourceSchema(value)
            if value.get('@type') == 'oa:Choice':
                return self._ImageResourceSchema(value['default'])
            raise Invalid("Image resource has unknown type: '{}'".format(value.get('@type')))

    return PatchedManifestSchema()


def get_vatlib_it_validator():
    class PatchedManifestSchema(FlexibleManifestSchema):
        def __init__(self):
            """Allow images to not have the required 'on' key."""
            super().__init__()

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
            return val

    return PatchedManifestSchema()


def get_stanford_edu_validator():
    class PatchedManifestSchema(FlexibleManifestSchema):
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
    class PatchedManifestSchema(FlexibleManifestSchema):
        def __init__(self):
            """Allow and correct 'type' instead of '@type' in images."""
            super().__init__()
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


def get_archivelab_org_importer():
    class PatchedManifestImporter(ManifestImporter):
        def _default_thumbnail_finder(self):
            """The internet archive thumbnail are enormous."""
            tn = self.json.get("thumbnail")
            if tn and isinstance(tn, str):
                return super()._default_thumbnail_finder(force_IIIF=True, index=0)
            else:
                return super()._default_thumbnail_finder()
    return PatchedManifestImporter


def get_gallica_bnf_fr_validator():
    class PatchedManifestSchema(FlexibleManifestSchema):
        def __init__(self):
            """Allow language key to not appear in some LangVal pairs."""
            super().__init__()
            self._LangValPairs = Schema(
                {
                    '@language': self.repeatable_string,
                    '@value': self.repeatable_string
                }
            )

        def metadata_type(self, value):
            """Correct any metadata entries missing a language key in lang-val pairs."""
            values = super().metadata_type(value)
            for value in values:
                v = value.get('value')
                if isinstance(v, list) and not all(vsub.get("@language") for vsub in v):
                    value['value'] = "; ".join((vsub.get("@value", "") for vsub in v))
            return values

    return PatchedManifestSchema()


def get_gallica_bnf_fr_importer():
    class PatchedManifestImporter(ManifestImporter):
        def _default_thumbnail_finder(self, force_IIIF=True):
            """The gallica thumbnails are very low res, so force it to pull out image."""
            return super()._default_thumbnail_finder(force_IIIF=True)
    return PatchedManifestImporter


def get_wdl_org_validator():
    class PatchedManifestSchema(FlexibleManifestSchema):
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

    # TODO Handle the keys that get missed in metadata.


class FlexibleManifestSchema(ManifestSchema):
    def __init__(self):
        super().__init__()

        self._CanvasSchema = Schema(
            {
                Required('@id'): self.http_uri,
                Required('@type'): 'sc:Canvas',
                Required('label'): self.str_or_val_lang,
                Required('height'): self.str_or_int,
                Required('width'): self.str_or_int,
                'images': self.images_in_canvas,
                'other_content': self.other_content
            },
            extra=ALLOW_EXTRA
        )

    def _run_validation(self, jdump):
        self.manifest = self.ManifestSchema(jdump)

    def uri_or_image_resource(self, value):
        if not value:
            return value
        return super().uri_or_image_resource(value)

    def str_or_int(self, value):
        if isinstance(value, str):
            try:
                val = int(value)
                self.warnings.add("Replaced string with int on height/width key.")
                return val
            except ValueError:
                raise Invalid("Str_or_int: {}".format(value))
        if isinstance(value, int):
            return value
        raise Invalid("Str_or_int: {}".format(value))
