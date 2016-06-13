from misirlou.helpers.schema_validator.manifest_schema import ManifestSchema
from voluptuous import Schema


def get_harvard_edu():
    # Append a context to the image services.
    def patched_service(self, value):
        if isinstance(value, str):
            return self.uri(value)
        elif isinstance(value, list):
            return [self.service(val) for val in value]
        else:
            val = self._Service(value)
            val['@context'] = 'http://library.stanford.edu/iiif/image-api/1.1/context.json'
            return val

    ManifestSchema.image_service = patched_service
    return ManifestSchema()
