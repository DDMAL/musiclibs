import urllib.parse

from voluptuous import Schema, Required, Invalid, MultipleInvalid, ALLOW_EXTRA


class ValidatorWarning(Invalid):
    pass


class ValidatorError(Invalid):
    pass


class BaseSchemaValidator:

    def __init__(self):
        self._manifest_schema = ManifestSchema
        self._image_resource_schema = ImageResourceSchema

        self.raise_warnings = True
        self.warnings = set()
        self.errors = []
        self.is_valid = None
        self.json = None

        self._LangValPairs = Schema(
            {
                Required('@language'): self.repeatable_string,
                Required('@value'): self.repeatable_string
            }
        )

    def validate(self, json_dict, raise_warnings=None):
        if raise_warnings is not None:
            self.raise_warnings = raise_warnings
        self.is_valid = None
        self.errors = []
        self.warnings = set()

        try:
            self._run_validation(json_dict)
            self.is_valid = True
            self.warnings = list(self.warnings)
        except MultipleInvalid as e:
            for err in e.errors:
                if isinstance(err, ValidatorError):
                    self.errors.append(e)
                if isinstance(err, ValidatorWarning):
                    self.warnings.add(e)
            if self.errors:
                self.is_valid = False
        except Exception as e:
            print("Unexpected validation error!")
            self.errors.append(e)
            self.is_valid = False

    def _run_validation(self, json_dict):
        self.json = json_dict
        self._main_schema(json_dict)

    def _handle_warnings(self, warning):
        if self.raise_warnings:
            raise warning

    @staticmethod
    def optional(fn):
        """Wrap a function to make its value optional"""
        def new_fn(*args):
            if args[0] == "" or args[0] is None:
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

class ManifestSchema(BaseSchemaValidator):
    PRESENTATION_API_URI = "http://iiif.io/api/presentation/2/context.json"
    IMAGE_API_1 = "http://library.stanford.edu/iiif/image-api/1.1/context.json"
    IMAGE_API_2 = "http://iiif.io/api/image/2/context.json"

    VIEW_DIRS = ['left-to-right', 'right-to-left',
                 'top-to-bottom', 'bottom-to-top']
    VIEW_HINTS = ['individuals', 'paged', 'continuous']

    def __init__(self):
        """Create a ManifestSchema validator."""
        super().__init__()
        self._manifest_schema = self.__class__

        # Schema for validating manifests with flexible corrections.
        self._main_schema = Schema(
            {
                # Descriptive properties
                Required('label'): self._label_field,
                '@context': self._presentation_context_field,
                'metadata': self.metadata_type,

                'description': self._description_field,
                'thumbnail': self._thumbnail_field,

                # Rights and Licensing properties
                'attribution': self.optional(self.str_or_val_lang),
                'logo': self.optional(self.uri_or_image_resource),
                'license': self.optional(self.repeatable_string),

                # Technical properties
                Required('@id'): self.http_uri,
                Required('@type'): 'sc:Manifest',
                'format': self.not_allowed,
                'height': self.not_allowed,
                'width': self.not_allowed,
                'viewingDirection': self.viewing_dir,
                'viewingHint': self.viewing_hint,

                # Linking properties
                'related': self.optional(self.repeatable_uri),
                'service': self.service,
                'seeAlso': self.optional(self.repeatable_uri),
                'within': self.optional(self.repeatable_uri),
                'startCanvas': self.not_allowed,
                Required('sequences'): self.manifest_sequence_list
            },
            extra=ALLOW_EXTRA
        )

    def _label_field(self, value):
        """Labels can be multi-value strings per 2.1-4.3"""
        return self.str_or_val_lang(value)

    def _presentation_context_field(self, value):
        if isinstance(value, str):
            if not value == self.PRESENTATION_API_URI:
                raise ValidatorError("@context must be set to {}".format(self.PRESENTATION_API_URI))
        if isinstance(value, list):
            if self.PRESENTATION_API_URI not in value:
                raise ValidatorError("@context must be set to {}".format(self.PRESENTATION_API_URI))
        return value

    def _description_field(self, value):
        return self.str_or_val_lang(value)

    def _metadata_field(self, value):
        """General type check for metadata.

        Recurse into keys/values and checks that they are properly formatted.
        """
        if isinstance(value, list):
            return [self._MetadataItem(val) for val in value]
        raise Invalid("Metadata is malformed.")

    def _thumbnail_field(self, value):
        if isinstance(value, str):
            raise ValidatorWarning("Thumbnail SHOULD be IIIF image service.")


    def metadata_type(self, value):
        """General type check for metadata.

        Recurse into keys/values and checks that they are properly formatted.
        """
        if isinstance(value, list):
            return [self._MetadataItem(val) for val in value]
        raise Invalid("Metadata is malformed.")



    def uri_or_image_resource(self, value):
        """Check value is URI or image_resource or raise Invalid.

        This is to be applied to Thumbnails, Logos, and other fields
        that could be a URI or image resource.
        """
        try:
            return self.repeatable_uri(value)
        except Invalid:
            return self.service(value)

    def image_service(self, value):
        """Validate against Service sub-schema."""
        if isinstance(value, str):
            return self.uri(value)
        elif isinstance(value, list):
            return [self.service(val) for val in value]
        else:
            return self._Service(value)

    def service(self, value):
        """Validate against Service sub-schema."""
        if isinstance(value, str):
            return self.uri(value)
        elif isinstance(value, list):
            return [self.service(val) for val in value]
        else:
            return self._Service(value)

    def service_profile(self, value):
        """Profiles in services are a special case.

        The profile key can contain a uri, or a list with extra
        metadata and a uri in the first position.
        """
        if isinstance(value, list):
            return self.uri(value[0])
        else:
            return self.uri(value)

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

    def manifest_sequence_list(self, value):
        """Validate sequence list for Manifest.

        Checks that exactly 1 sequence is embedded.
        """
        if not isinstance(value, list):
            raise Invalid("'sequences' must be a list")
        lst = [self._EmbSequenceSchema(value[0])]
        lst.extend([self._LinkedSequenceSchema(s) for s in value[1:]])
        return lst

    def sequence_canvas_list(self, value):
        """Validate canvas list for Sequence."""
        if not isinstance(value, list):
            raise Invalid("'canvases' must be a list")
        return [self._CanvasSchema(c) for c in value]

    def images_in_canvas(self, value):
        """Validate images list for Canvas"""
        if isinstance(value, list):
            return [self._ImageSchema(i) for i in value]
        if not value:
            return
        raise Invalid("'images' must be a list")

    def image_resource(self, value):
        """Validate image resources inside images list of Canvas"""
        if value.get('@type') == "dctypes:Image":
            return self._ImageResourceSchema(value)
        if value.get('@type') == 'oa:Choice':
            return self._ImageResourceSchema(value['default'])
        raise Invalid("Image resource has unknown type: '{}'".format(value))

    def other_content(self, value):
        if not isinstance(value, list):
            raise Invalid("other_content must be list!")
        return [self.uri(item['@id']) for item in value]


class SequenceSchema(BaseSchemaValidator):
    pass

class CanvasSchema(BaseSchemaValidator):
    pass

class ImageResourceSchema(BaseSchemaValidator):

    def __init__(self):
        super().__init__()

        self._ImageSchema = Schema(
            {
                "@id": self.http_uri,
                Required('@type'): "oa:Annotation",
                Required('motivation'): "sc:painting",
                Required('resource'): self.image_resource,
                Required("on"): self.http_uri
            }, extra=ALLOW_EXTRA
        )

    def _id_field(self, value):
        pass
