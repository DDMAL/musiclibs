"""This module defines special handling for manifests from specific libraries.

All functions should return a ManifestSchema() instance to be used by the
validator.

These functions specify exceptions and corrections to be made during validation
based on the systematic faults of manifests hosted by specific libraries. They
do this by patching the ManifestSchema class with overriding behaviour before
instantiating a newly patched ManifestSchema and returning it.

If possible (e.g., if all that is required is adding/removing/modifying the
return value of a particular section), the original function should be called
and changes applied afterwards (see get_harvard_edu.patched_image_service).

The patched function should, if possible, check that the error it is designed
to correct is still present before making modifications. This way, if the
library eventually corrects their manifests, re-importing will not result in
erroneous corrections.
"""
from misirlou.helpers.schema_validator.manifest_schema import ManifestSchema

def get_harvard_edu():
    # Append a context to the image services.
    class PatchedManifestSchema(ManifestSchema):
        def image_service(self, value):
            val = super().image_service(value)
            if not val.get('@context'):
                val['@context'] = 'http://library.stanford.edu/iiif/image-api/1.1/context.json'
            return val
    return PatchedManifestSchema()

