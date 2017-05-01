"""This module defines special handling for manifests from specific libraries.

All functions should return a IIIFValidator() instance to be used by the
validator.

These functions specify exceptions and corrections to be made during validation
and indexing based on the systematic faults of manifests hosted by specific libraries.
They do this by patching subclassing resource validators, creating them, then
passing them into a IIIFValidator for use.

Functions which return IIIFValidators should be named get_[netloc]_validator,
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
import urllib.parse

from misirlou.helpers.manifest_utils.importer import ManifestImporter
from tripoli import IIIFValidator, ManifestValidator, CanvasValidator, AnnotationValidator, SequenceValidator
from tripoli.resource_validators.image_content_validator import ImageContentValidator
from tripoli.resource_validators.base_validator import BaseValidator


def get_harvard_edu_validator():
    def str_to_int(self, field, value):
        """Coerce strings to ints."""
        if isinstance(value, int):
            return value
        try:
            val = int(value)
            self.log_warning(field, "Coerced to int.")
            return val
        except ValueError:
            self.log_error(field, "Could not coerce to int.")
            return value

    BaseValidator.width_field = lambda self, value: str_to_int(self, "width", value)
    BaseValidator.height_field = lambda self, value: str_to_int(self, "height", value)

    class PatchedImageContentValidator(ImageContentValidator):
        def service_field(self, value):
            """Add a context to the service if none exists."""
            val, errs = self.mute_errors(super().service_field, value)
            if not val.get('@context'):
                val['@context'] = 'http://library.stanford.edu/iiif/image-api/1.1/context.json'
                self.log_warning("@context", "Applied library specific corrections. Added @context to images.")
            return val

        def type_field(self, value):
            if value == 'dcterms:Image':
                self.log_warning('@type', 'Coerced type to correct value.')
            return 'dctypes:Image'

    class PatchedManifestValidator(ManifestValidator):
        @ManifestValidator.errors_to_warnings
        def context_field(self, value):
            """Allow the unknown top level context (since it doesn't seem to break things)"""
            return super().context_field(value)

        @ManifestValidator.errors_to_warnings
        def license_field(self, value):
            """Allow non uri in license field."""

            return super().license_field(value)

    iv = IIIFValidator()
    iv.ManifestValidator = PatchedManifestValidator
    iv.ImageContentValidator = PatchedImageContentValidator
    return iv


def get_vatlib_it_validator():
    class PatchedAnnotationValidator(AnnotationValidator):
        def setup(self):
            self.REQUIRED_FIELDS = AnnotationValidator.REQUIRED_FIELDS - {"on"}
            self.RECOMMENDED_FIELDS = AnnotationValidator.RECOMMENDED_FIELDS | {"on"}

    class PatchedCanvasValidator(CanvasValidator):
        def viewing_hint_field(self, value):
            val, errs = self.mute_errors(super().viewing_hint_field, value)
            if errs:
                if val == "paged":
                    self.log_warning("viewingHint", "Applied library specific corrections. Allowed value 'paged'.")

    iv = IIIFValidator()
    iv.AnnotationValidator = PatchedAnnotationValidator
    iv.CanvasValidator = PatchedCanvasValidator
    return iv


def get_stanford_edu_validator():
    return get_harvard_edu_validator()


def get_archivelab_org_validator():
    class PatchedManifestValidator(ManifestValidator):
        # Replace the image API with the presentation API at manifest level.
        def context_field(self, value):
            if value == 'http://iiif.io/api/image/2/context.json':
                self.log_warning("@context", "Applied library specific corrections. "
                                                 "Replaced image context with presentation context.")
                return self.PRESENTATION_API_URI
            return value

    class PatchedSequenceValidator(SequenceValidator):
        @SequenceValidator.errors_to_warnings
        def context_field(self, value):
            return super().context_field(value)

    class PatchedAnnotationValidator(AnnotationValidator):
        REQUIRED_FIELDS = AnnotationValidator.REQUIRED_FIELDS - {"on", "@type"}

        def setup(self):
            self.ImageSchema['type'] = self.type_field

    iv = IIIFValidator()
    iv.ManifestValidator = PatchedManifestValidator
    iv.AnnotationValidator = PatchedAnnotationValidator
    iv.SequenceValidator = PatchedSequenceValidator
    return iv


def get_archivelab_org_importer():
    class PatchedManifestImporter(ManifestImporter):
        def _default_thumbnail_finder(self):
            """The internet archive thumbnail are enormous."""
            tn = self.json.get("thumbnail")
            return super()._default_thumbnail_finder(force_IIIF=True, index=0)
    return PatchedManifestImporter


def get_gallica_bnf_fr_validator():

    class PatchedManifestValidator(ManifestValidator):
        # Squash the lang-val pairs down to one value, separated by semicolon.

        def metadata_field(self, value):

            """Correct any metadata entries missing a language key in lang-val pairs."""
            values, errs = self.mute_errors(super().metadata_field, value)
            if not errs:
                return values
            for value in values:
                v = value.get('value')
                if isinstance(v, list) and not all(vsub.get("@language") for vsub in v):
                    value['value'] = "; ".join((vsub.get("@value", "") for vsub in v))
                    self.log_warning("metadata", "Applied library specific corrections: "
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


def get_validator(uri):
    """Configure a schemas based on settings relevant to given uri."""

    parsed = urllib.parse.urlparse(uri)
    netloc = parsed.netloc
    if netloc == "iiif.lib.harvard.edu":
        return get_harvard_edu_validator()
    if netloc == "digi.vatlib.it":
        return get_vatlib_it_validator()
    if netloc == "purl.stanford.edu":
        return get_stanford_edu_validator()
    if netloc == "iiif.archivelab.org":
        return get_archivelab_org_validator()
    if netloc == "gallica.bnf.fr":
        return get_gallica_bnf_fr_validator()
    if netloc == "www.wdl.org":
        return get_wdl_org_validator()

    return IIIFValidator()
