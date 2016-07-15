"""This module defines special handling for manifests from specific libraries.

All functions should return a ManifestValidator() instance to be used by the
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
from misirlou.helpers.manifest_utils.schema_validator import ManifestValidator, ImageResourceValidator, ValidatorError, \
    SequenceValidator, IIIFValidator, CanvasValidator
from voluptuous import Schema, Required, ALLOW_EXTRA, Invalid


def get_harvard_edu_validator():
    class PatchedImageResourceValidator(ImageResourceValidator):

        # Append a context to the image services if none exist.
        def _image_service_field(self, value):
            val = super()._image_service_field(value)
            if not val.get('@context'):
                val['@context'] = 'http://library.stanford.edu/iiif/image-api/1.1/context.json'
                self._handle_warning("@context", "Applied library specific corrections. Added @context to images.")
            return val

        # Allow @type to be 'dcterms:Image'
        def _image_resource_field(self, value):
            if value.get('@type') in "dctypes:Image":
                return self.ImageResourceSchema(value)
            if value.get('@type') == "dcterms:Image":
                self._handle_warning("@type", "Applied library specific corrections. Allowed 'dcterms:Image'.")
                value['@type'] = 'dctypes:Image'
                return self.ImageResourceSchema(value)
            if value.get('@type') == 'oa:Choice':
                return self.ImageResourceSchema(value['default'])
            raise Invalid("Image resource has unknown type: '{}'".format(value.get('@type')))

    class PatchedManifestValidator(FlexibleManifestValidator):

        # Allow the unknown top level context (since it doesn't seem to break things")
        def presentation_context_field(self, value):
            try:
                return super().ManifestValidator(value)
            except Invalid:
                self._handle_warning("@context", "Unknown context.")
                return value

    iv = IIIFValidator()
    iv.ManifestValidator = PatchedManifestValidator
    iv.ImageResourceValidator = PatchedImageResourceValidator
    return iv


def get_vatlib_it_validator():
    class PatchedImageResourceValidator(ImageResourceValidator):

        # Alter ImageSchema to not really check the 'on' key.
        def _setup(self):
            super()._setup()
            self.ImageSchema = Schema(
                {
                    "@id": self._http_uri_type,
                    Required('@type'): "oa:Annotation",
                    Required('motivation'): "sc:painting",
                    Required('resource'): self._image_resource_field,
                    "on": self._http_uri_type
                }, extra=ALLOW_EXTRA
            )

        def modify_validation_return(self, json_dict):
            if not json_dict.get('on'):
                self._handle_warning("on", "Applied library specific corrections. Key requirement ignored.")
            return json_dict

    iv = IIIFValidator()
    iv.ImageResourceValidator = PatchedImageResourceValidator
    return iv


def get_stanford_edu_validator():
    return get_harvard_edu_validator()


def get_archivelab_org_validator():
    class PatchedManifestValidator(FlexibleManifestValidator):

        # Replace the image API with the presentation API at manifest level.
        def presentation_context_field(self, value):
            if value == 'http://iiif.io/api/image/2/context.json':
                self._handle_warning("@context", "Applied library specific corrections. "
                                                 "Replaced image context with presentation context.")
                return self.PRESENTATION_API_URI
            return value

    class PatchedSequenceValidator(SequenceValidator):

        # Allow the @context key in the embedded sequence.
        def _setup(self):
            super()._setup()
            self.EmbSequenceSchema = Schema(
                {
                    Required('@type'): 'sc:Sequence',
                    '@id': self._http_uri_type,
                    '@context': self.bad_context_key,
                    'label': self._str_or_val_lang_type,
                    'startCanvas': self._uri_type,
                    Required('canvases'): self._canvases_field,
                    'viewingDirection': self._viewing_direction_field,
                    'viewingHint': self._viewing_hint_field
                },
                extra=ALLOW_EXTRA
            )

        def bad_context_key(self, value):
            self._handle_warning('@context', "Applied library specific corrections."
                                             "'@context' must not exist in embedded sequence.")
            return value

    class PatchedImageResourceValidator(ImageResourceValidator):

        # Allow 'type' in place of '@type' field.
        def _setup(self):
            super()._setup()
            self.ImageSchema = Schema(
                {
                    "@id": self._http_uri_type,
                    '@type': "oa:Annotation",
                    'type': "oa:Annotation",
                    Required('motivation'): "sc:painting",
                    Required('resource'): self._image_resource_field,
                    "on": self._http_uri_type
                }, extra=ALLOW_EXTRA
            )

        # Replace the 'type' key with '@type'.
        def modify_validation_return(self, validation_results):
            if 'type' in validation_results:
                validation_results['@type'] = validation_results['type']
                del validation_results['type']
            return validation_results

    iv = IIIFValidator()
    iv.ManifestValidator = PatchedManifestValidator
    iv.ImageResourceValidator = PatchedImageResourceValidator
    iv.SequenceValidator = PatchedSequenceValidator
    return iv


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

    class PatchedManifestValidator(ManifestValidator):
        # Squash the lang-val pairs down to one value, separated by semicolon.

        def _metadata_field(self, value):
            """Correct any metadata entries missing a language key in lang-val pairs."""
            self._LangValPairs = Schema({
                "@language": self._str_or_val_lang_type,
                "@value": self._str_or_val_lang_type
            })
            values = super()._metadata_field(value)
            for value in values:
                v = value.get('value')
                if isinstance(v, list) and not all(vsub.get("@language") for vsub in v):
                    value['value'] = "; ".join((vsub.get("@value", "") for vsub in v))
                    self._handle_warning("metadata", "Applied library specific corrections: "
                                                     "metadata field bad formatting ignored.")
            return values

    iv = IIIFValidator()
    iv.ManifestValidator = PatchedManifestValidator
    return iv


def get_gallica_bnf_fr_importer():
    class PatchedManifestImporter(ManifestImporter):
        def _default_thumbnail_finder(self, force_IIIF=True):
            """The gallica thumbnails are very low res, so force it to pull out image."""
            return super()._default_thumbnail_finder(force_IIIF=True)
    return PatchedManifestImporter


def get_wdl_org_validator():
    return get_harvard_edu_validator()


# General flexible manifest validator.
class FlexibleCanvasValidator(CanvasValidator):
    def str_or_int(self, value):
        if isinstance(value, str):
            try:
                val = int(value)
                self._handle_warning("height/width", "Replaced string with int on height/width key.")
                return val
            except ValueError:
                raise ValidatorError("Str_or_int: {}".format(value))
        if isinstance(value, int):
            return value
        raise ValidatorError("Str_or_int: {}".format(value))

    def _setup(self):
        super()._setup()
        self._raise_warnings = True
        self.CanvasValidator.CanvasSchema = Schema(
            {
                Required('@id'): self._http_uri_type,
                Required('@type'): 'sc:Canvas',
                Required('label'): self._str_or_val_lang_type,
                Required('height'): self.str_or_int,
                Required('width'): self.str_or_int,
                'images': self._images_field,
                'other_content': self._other_content_field
            },
            extra=ALLOW_EXTRA
        )


class FlexibleManifestValidator(ManifestValidator):
    def _setup(self):
        super()._setup()
        self.CanvasValidator = FlexibleCanvasValidator


class FlexibleValidator(IIIFValidator):
    def __init__(self):
        super().__init__()
        self.ManifestValidator = FlexibleManifestValidator
