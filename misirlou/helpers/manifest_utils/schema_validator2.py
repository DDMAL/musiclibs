import urllib.parse
import pdb
from voluptuous import Schema, Required, Invalid, MultipleInvalid, ALLOW_EXTRA


class ValidatorWarning(Invalid):
    pass


class BaseIIIFValidatorMixin:

    def __init__(self):
        """You should NOT override ___init___. Override setup() instead."""
        self.raise_warnings = True
        self.warnings = set()
        self.errors = []
        self.is_valid = None
        self.json = None
        self.SequenceValidator = None
        self.ImageResourceValidator = None
        self.CanvasValidator = None
        self._LangValPairs = None
        self.setup()

    def setup(self):
        self._LangValPairs = Schema(
            {
                Required('@language'): self.repeatable_string,
                Required('@value'): self.repeatable_string
            }
        )

    def validate(self, json_dict, raise_warnings=None, **kwargs):
        """Public method to run validation."""
        if raise_warnings is not None:
            self.raise_warnings = raise_warnings

        self.__inheritance_fix()
        self.is_valid = None
        self.errors = []
        self.warnings = set()

        try:
            self.json = json_dict
            self._run_validation(**kwargs)
            self.is_valid = True
        except MultipleInvalid as e:
            for err in e.errors:
                if isinstance(err, ValidatorWarning):
                    self.warnings.add(e)
                else:
                    self.errors.append(e)
            if self.errors:
                self.is_valid = False
        except Exception as e:
            print("Unexpected validation error!")
            self.errors.append(e)
            self.is_valid = False

    def __inheritance_fix(self):
        """Fix to make sure we have references to all sub-schemas at validation."""
        if self.SequenceValidator is None:
            self.SequenceValidator = self.manifest_validator.SequenceValidator
        if self.ImageResourceValidator is None:
            self.ImageResourceValidator = self.manifest_validator.ImageResourceValidator
        if self.CanvasValidator is None:
            self.CanvasValidator = self.manifest_validator.CanvasValidator

    def _run_validation(self, **kwargs):
        raise NotImplemented

    def _handle_warnings(self, warning):
        if self.raise_warnings:
            raise ValidatorWarning(warning)

    def _sub_validate(self, subschema, value, **kwargs):
        subschema.validate(value, **kwargs)
        if subschema.warnings:
            self.warnings = self.warnings.union(subschema.warnings)
        if subschema.errors:
            self.errors.extend(subschema.errors)
        return subschema.json

    def optional(self, field, fn):
        """Wrap a function to make its value optional"""
        def new_fn(*args):
            if args[0] == "" or args[0] is None:
                self.warnings.add("'{}' field should not be included if it is empty.".format(field))
                return args[0]
            return fn(*args)
        return new_fn

    def not_allowed(self, value):
        """Raise invalid as this key is not allowed in the context."""
        raise Invalid("Key is not allowed here.")

    def str_or_val_lang(self, value):
        """Check value is str or lang/val pairs, else raise Invalid.

        Allows for repeated strings as per 5.3.2.
        """

        if isinstance(value, str):
            return value
        if isinstance(value, list):
            return [self.str_or_val_lang(val) for val in value]
        if isinstance(value, dict):
            return self._LangValPairs(value)
        raise Invalid("Str_or_val_lang: {}".format(value))

    def repeatable_string(self, value):
        """Allows for repeated strings as per 5.3.2."""
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            for val in value:
                if not isinstance(val, str):
                    raise Invalid("Overly nested strings: {}".format(value))
            return value
        raise Invalid("repeatable_string: {}".format(value))

    def repeatable_uri(self, value):
        """Allow single or repeating URIs.

        Based on 5.3.2 of Presentation API
        """
        if isinstance(value, list):
            return [self.uri(val) for val in value]
        else:
            return self.uri(value)

    def http_uri(self, value):
        """Allow single URI that MUST be http(s)

        Based on 5.3.2 of Presentation API
        """
        return self.uri(value, http=True)

    def uri(self, value, http=False):
        """Check value is URI type or raise Invalid.

        Allows for multiple URI representations, as per 5.3.1 of the
        Presentation API.
        """
        if isinstance(value, str):
            return self._string_uri(value, http)
        elif isinstance(value, dict):
            emb_uri = value.get('@id')
            if not emb_uri:
                raise Invalid("URI not found: {} ".format(value))
            return self._string_uri(emb_uri, http)
        else:
            raise Invalid("Can't parse URI: {}".format(value))

    def _string_uri(self, value, http=False):
        """Validate that value is a string that can be parsed as URI.

        This is the last stop on the recursive structure for URI checking.
        Should not actually be used in schema.
        """
        # Always raise invalid if the string field is not a string.
        if not isinstance(value, str):
            raise Invalid("URI is not String: {]".format(value))
        # Try to parse the url.
        try:
            pieces = urllib.parse.urlparse(value)
        except AttributeError as a:
            raise Invalid("URI is not valid: {}".format(value))
        if not all([pieces.scheme, pieces.netloc]):
            raise Invalid("URI is not valid: {}".format(value))
        if http and pieces.scheme not in ['http', 'https']:
            raise Invalid("URI must be http: {}".format(value))
        return value


class ManifestValidator(BaseIIIFValidatorMixin):
    PRESENTATION_API_URI = "http://iiif.io/api/presentation/2/context.json"
    IMAGE_API_1 = "http://library.stanford.edu/iiif/image-api/1.1/context.json"
    IMAGE_API_2 = "http://iiif.io/api/image/2/context.json"

    VIEW_DIRS = ['left-to-right', 'right-to-left',
                 'top-to-bottom', 'bottom-to-top']
    VIEW_HINTS = ['individuals', 'paged', 'continuous']

    def __init__(self):
        """You should not override ___init___. Override setup() instead."""
        super().__init__()
        self.manifest_validator = self
        self.ManifestSchema = None
        self.MetadataItemSchema = None
        self.setup()

    def setup(self):
        self.ImageResourceValidator = ImageResourceValidator(self)
        self.CanvasValidator = CanvasValidator(self)
        self.SequenceValidator = SequenceValidator(self)

        # Schema for validating manifests with flexible corrections.
        self.ManifestSchema = Schema(
            {
                # Descriptive properties
                Required('label'): self._label_field,
                '@context': self._presentation_context_field,
                'metadata': self._metadata_field,

                'description': self._description_field,
                'thumbnail': self._thumbnail_field,

                # Rights and Licensing properties
                'attribution': self.optional('attribution', self.str_or_val_lang),
                'logo': self.optional('logo', self.repeatable_uri),
                'license': self.optional('license', self.repeatable_string),

                # Technical properties
                Required('@id'): self.http_uri,
                Required('@type'): 'sc:Manifest',
                'format': self.not_allowed,
                'height': self.not_allowed,
                'width': self.not_allowed,
                'viewingDirection': self.viewing_dir,
                'viewingHint': self.viewing_hint,

                # Linking properties
                'related': self.optional('related', self.repeatable_uri),
                'service': self.optional('service', self.repeatable_uri),
                'seeAlso': self.optional('seeAlso', self.repeatable_uri),
                'within': self.optional('within', self.repeatable_uri),
                'startCanvas': self.not_allowed,
                Required('sequences'): self.sequences_field
            },
            extra=ALLOW_EXTRA
        )
        self.MetadataItemSchema = Schema(
            {
                'label': self.str_or_val_lang,
                'value': self.str_or_val_lang
            }
        )

    def _run_validation(self, **kwargs):
        return self.ManifestSchema(self.json)

    def _label_field(self, value):
        """Labels can be multi-value strings per 2.1-4.3"""
        return self.str_or_val_lang(value)

    def _presentation_context_field(self, value):
        if isinstance(value, str):
            if not value == self.PRESENTATION_API_URI:
                raise Invalid("@context must be set to {}".format(self.PRESENTATION_API_URI))
        if isinstance(value, list):
            if self.PRESENTATION_API_URI not in value:
                raise Invalid("@context must be set to {}".format(self.PRESENTATION_API_URI))
        return value

    def _description_field(self, value):
        return self.str_or_val_lang(value)

    def _metadata_field(self, value):
        """General type check for metadata.

        Recurse into keys/values and checks that they are properly formatted.
        """
        if isinstance(value, list):
            return [self.MetadataItemSchema(val) for val in value]
        raise Invalid("Metadata key MUST be a list.")

    def _thumbnail_field(self, value):
        if isinstance(value, str):
            self._handle_warnings("Thumbnail SHOULD be IIIF image service.")
            return self.uri(value)
        if isinstance(value, dict):
            return self._sub_validate(self.ImageResourceValidator, value)

        # TODO complete this function.

    def viewing_dir(self, value):
        """Validate against VIEW_DIRS list."""
        if value not in self.VIEW_DIRS:
            raise Invalid("viewingDirection: {}".format(value))
        return value

    def viewing_hint(self, value):
        """Validate against VIEW_HINTS list."""
        if value not in self.VIEW_HINTS:
            raise Invalid("viewingHint: {}".format(value))
        return value

    def sequences_field(self, value):
        """Validate sequence list for Manifest.

        Checks that exactly 1 sequence is embedded.
        """
        return self._sub_validate(self.SequenceValidator, value)


class SequenceValidator(BaseIIIFValidatorMixin):
    def __init__(self, manifest_validator):
        """You should not override ___init___. Override setup() instead."""
        super().__init__()
        self.manifest_validator = manifest_validator
        self.EmbSequenceSchema = None
        self.LinkedSequenceSchema = None
        self.CanvasValidator = manifest_validator.CanvasValidator
        self.setup()

    def setup(self):

        # An embedded sequence must contain canvases.
        self.EmbSequenceSchema = Schema(
            {
                Required('@type'): 'sc:Sequence',
                '@id': self.http_uri,
                'label': self.str_or_val_lang,
                Required('canvases'): self.canvas_list
            },
            extra=ALLOW_EXTRA
        )

        # A linked sequence must have an @id and no canvases
        self.LinkedSequenceSchema = Schema(
            {
                Required('@type'): 'sc:Sequence',
                Required('@id'): self.http_uri,
                'canvases': self.not_allowed
            },
            extra=ALLOW_EXTRA
        )

    def _run_validation(self, **kwargs):
        return self._validate_sequence()

    def _validate_sequence(self):
        value = self.json
        if not isinstance(value, list):
            raise Invalid("'sequences' must be a list.")
        lst = [self.EmbSequenceSchema(value[0])]
        lst.extend([self.LinkedSequenceSchema(s) for s in value[1:]])
        return lst

    def canvas_list(self, value):
        """Validate canvas list for Sequence."""
        if not isinstance(value, list):
            raise Invalid("'canvases' must be a list")
        return [self._sub_validate(self.CanvasValidator, c) for c in value]


class CanvasValidator(BaseIIIFValidatorMixin):
    def __init__(self, manifest_validator):
        """You should not override ___init___. Override setup() instead."""
        super().__init__()

        self.manifest_validator = manifest_validator
        self.CanvasSchema = None
        self.setup()

    def setup(self):
        self.CanvasSchema = Schema(
            {
                Required('@id'): self.http_uri,
                Required('@type'): 'sc:Canvas',
                Required('label'): self.str_or_val_lang,
                Required('height'): int,
                Required('width'): int,
                'images': self.images_field,
                'other_content': self.other_content_field
            },
            extra=ALLOW_EXTRA
        )

    def _run_validation(self, **kwargs):
        self.canvas_uri = self.json['@id']
        return self.CanvasSchema(self.json)

    def images_field(self, value):
        if isinstance(value, list):
            return [self._sub_validate(self.ImageResourceValidator, i, canvas_uri=self.canvas_uri) for i in value]
        if not value:
            return
        raise Invalid("'images' must be a list")

    def other_content_field(self, value):
        if not isinstance(value, list):
            raise Invalid("other_content must be list!")
        return [self.uri(item['@id']) for item in value]


class ImageResourceValidator(BaseIIIFValidatorMixin):

    def __init__(self, manifest_validator):
        """You should not override ___init___. Override setup() instead."""
        super().__init__()

        self.manifest_validator = manifest_validator
        self.ImageSchema = None
        self.ImageResourceSchema = None
        self.ServiceSchema = None
        self.canvas_uri = None
        self.setup()

    def setup(self):
        self.ImageSchema = Schema(
            {
                "@id": self.http_uri,
                Required('@type'): "oa:Annotation",
                Required('motivation'): "sc:painting",
                Required('resource'): self.image_resource,
                Required("on"): self._on_field
            }, extra=ALLOW_EXTRA
        )
        self.ImageResourceSchema = Schema(
            {
                Required('@id'): self.http_uri,
                '@type': 'dctypes:Image',
                "service": self.image_service
            }, extra=ALLOW_EXTRA
        )

        self.ServiceSchema = Schema(
            {
                '@context': self.repeatable_string,
                '@id': self.uri,
                'profile': self.service_profile,
                'label': str
            },
            extra=ALLOW_EXTRA
        )

    def _run_validation(self, canvas_uri=None, **kwargs):
        self.canvas_uri = canvas_uri
        return self.ImageSchema(self.json)

    def _id_field(self, value):
        pass

    def _on_field(self, value):
        if value != self.canvas_uri:
            raise Invalid("'On' must reference the canvas URI.")

    def image_resource(self, value):
        """Validate image resources inside images list of Canvas"""
        if value.get('@type') == "dctypes:Image":
            return self.ImageResourceSchema(value)
        if value.get('@type') == 'oa:Choice':
            return self.ImageResourceSchema(value['default'])
        raise Invalid("Image resource has unknown type: '{}'".format(value))

    def image_service(self, value):
        """Validate against Service sub-schema."""
        if isinstance(value, str):
            return self.uri(value)
        elif isinstance(value, list):
            return [self.service(val) for val in value]
        else:
            return self.ServiceSchema(value)

    def service(self, value):
        """Validate against Service sub-schema."""
        if isinstance(value, str):
            return self.uri(value)
        elif isinstance(value, list):
            return [self.service(val) for val in value]
        else:
            return self.ServiceSchema(value)

    def service_profile(self, value):
        """Profiles in services are a special case.

        The profile key can contain a uri, or a list with extra
        metadata and a uri in the first position.
        """
        if isinstance(value, list):
            return self.uri(value[0])
        else:
            return self.uri(value)

if __name__ == "__main__":
    import requests
    import IPython
    man = requests.get("http://dev-cantus.simssa.ca/manuscript/133/manifest.json").json()
    mv = ManifestValidator()
    IPython.embed()
