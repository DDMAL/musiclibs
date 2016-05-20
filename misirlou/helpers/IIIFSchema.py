from voluptuous import Schema, Required, Invalid, ALLOW_EXTRA
import urllib.parse

VIEW_DIRS = ['left-to-right', 'right-to-left',
             'top-to-bottom', 'bottom-to-top']
VIEW_HINTS = ['individuals', 'paged', 'continuous']


def not_allowed(value):
    """Raise invalid as this key is not allowed in the context."""
    raise Invalid("Key is not allowed here.")


def str_or_int(value):
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            raise Invalid("Str_or_int: {}".format(value))
    if isinstance(value, int):
        return value
    raise Invalid("Str_or_int: {}".format(value))


def str_or_val_lang(value):
    """Check value is str or lang/val pairs, else raise Invalid.

    Allows for repeated strings as per 5.3.2.
    """
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return [str_or_val_lang(val) for val in value]
    if isinstance(value, dict):
        return _lang_val_pairs(value)
    raise Invalid("Str_or_val_lang: {}".format(value))


def repeatable_string(value):
    """Allows for repeated strings as per 5.3.2."""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        for val in value:
            if not isinstance(val, str):
                raise Invalid("Overly nested strings: {}".format(value))
        return value
    raise Invalid("repeatable_string: {}".format(value))


def metadata_type(value):
    """General type check for metadata.

    Recurse into keys/values and checks that they are properly formatted.
    """
    if isinstance(value, list):
        return [metadata_item(val) for val in value]
    raise Invalid("Metadata is malformed.")

"""Sub-schema for checking items in the metadata list."""
metadata_item = Schema(
    {
        'label': str_or_val_lang,
        'value': str_or_val_lang
    }
)


def repeatable_uri(value):
    """Allow single or repeating URIs.

    Based on 5.3.2 of Presentation API
    """
    if isinstance(value, list):
        return [uri(val) for val in value]
    else:
        return uri(value)

    return value


def http_uri(value):
    """Allow single URI that MUST be http(s)

    Based on 5.3.2 of Presentation API
    """
    return uri(value, http=True)


def uri(value, http=False):
    """Check value is URI type or raise Invalid.

    Allows for multiple URI representations, as per 5.3.1 of the
    Presentation API.
    """
    if isinstance(value, str):
        return _string_uri(value, http)
    elif isinstance(value, dict):
        emb_uri = value.get('@id')
        if not emb_uri:
            raise Invalid("URI not found: {} ".format(value))
        return _string_uri(emb_uri, http)
    else:
        raise Invalid("Can't parse URI: {}".format(value))


def _string_uri(value, http=False):
    """Validate that value is a string that can be parsed as URI.

    This is the last stop on the recursive structure for URI checking.
    Should not actually be used in schema.
    """
    if not isinstance(value, str):
        raise Invalid("URI is not String: {]".format(value))
    try:
        pieces = urllib.parse.urlparse(value)
    except AttributeError as a:
        raise Invalid("URI is not valid: {}".format(value))
    if not all([pieces.scheme, pieces.netloc]):
        raise Invalid("URI is not valid: {}".format(value))
    if http and pieces.scheme not in ['http', 'https']:
        raise Invalid("URI must be http: {}".format(value))
    return value


def uri_or_image_resource(value):
    """Check value is URI or image_resource or raise Invalid.

    This is to be applied to Thumbnails, Logos, and other fields
    that could be a URI or image resource.
    """
    try:
        return repeatable_uri(value)
    except Invalid:
        return service(value)


def service(value):
    """Validate against Service sub-schema."""
    if isinstance(value, str):
        return uri(value)
    elif isinstance(value, list):
        return [service(val) for val in value]
    else:
        return _service_sub(value)


def service_profile(value):
    """Profiles in services are a special case.

    The profile key can contain a uri, or a list with extra
    metadata and a uri in the first position.
    """
    if isinstance(value, list):
        return uri(value[0])
    else:
        return uri(value)

"""Sub-schema for services."""
_service_sub = Schema(
    {
        Required('@context'): uri,
        '@id': uri,
        'profile': service_profile,
        'label': str
    },
    extra=ALLOW_EXTRA
)


def viewing_dir(value):
    """Validate against VIEW_DIRS list."""
    if value not in VIEW_DIRS:
        raise Invalid("viewingDirection: {}".format(value))
    return value


def viewing_hint(value):
    """Validate against VIEW_HINTS list."""
    if value not in VIEW_HINTS:
        raise Invalid("viewingHint: {}".format(value))
    return value


def manifest_sequence_list(value):
    """Validate sequence list for Manifest.

    Checks that exactly 1 sequence is embedded.
    """
    if not isinstance(value, list):
        raise Invalid("'sequences' must be a list")
    lst = [_EmbSequenceSchema(value[0])]
    lst.extend([_LinkedSequenceSchema(s) for s in value[1:]])
    return lst

def sequence_canvas_list(value):
    """Validate canvas list for Sequence."""
    if not isinstance(value, list):
        raise Invalid("'canvases' must be a list")
    return [_CanvasSchema(c) for c in value]


def images_in_canvas(value):
    """Validate images list for Canvas"""
    if isinstance(value, list):
        return [_ImageSchema(i) for i in value]
    if not value:
        return
    raise Invalid("'images' must be a list")


def image_resource(value):
    """Validate image resources inside images list of Canvas"""
    if value['@type'] == "dctypes:Image":
        return _ImageResourceSchema(value)
    if value['@type'] == 'oa:Choice':
        return _ImageResourceSchema(value['default'])


def other_content(value):
    if not isinstance(value, list):
        raise Invalid("other_content must be list!")
    return [uri(item['@id']) for item in value]

"""Sub-schema for lang-val pairs which can stand in for some stings.
   as defined in 5.3.3."""
_lang_val_pairs = Schema(
    {
        '@language': repeatable_string,
        '@value': repeatable_string
    }
)


# Schema for Images
_ImageSchema = Schema(
    {
        "@id": http_uri,
        Required('@type'): "oa:Annotation",
        Required('motivation'): "sc:painting",
        Required('resource'): image_resource,
        "on": http_uri
    }, extra=ALLOW_EXTRA
)

_ImageResourceSchema = Schema(
    {
        Required('@id'): http_uri,
        '@type': 'dctypes:Image',
        "service": service
    }, extra=ALLOW_EXTRA
)

# Schema for Canvases.
_CanvasSchema = Schema(
    {
        Required('@id'): http_uri,
        Required('@type'): 'sc:Canvas',
        Required('label'): str_or_val_lang,
        Required('height'): str_or_int,
        Required('width'): str_or_int,
        'images': images_in_canvas,
        'other_content': other_content
    },
    extra=ALLOW_EXTRA
)

# An embedded sequence must contain canvases.
_EmbSequenceSchema = Schema(
    {
        Required('@type'): 'sc:Sequence',
        '@id': http_uri,
        'label': str_or_val_lang,
        Required('canvases'): sequence_canvas_list
    },
    extra=ALLOW_EXTRA
)

# A linked sequence must have an @id and no canvases
_LinkedSequenceSchema = Schema(
    {
        Required('@type'): 'sc:Sequence',
        Required('@id'): http_uri,
        'canvases': not_allowed
    },
    extra=ALLOW_EXTRA
)

# Schema for validating manifests.
ManifestSchema = Schema(
    {
        # Descriptive properties
        Required('label'): str_or_val_lang,
        '@context': http_uri,
        'metadata': metadata_type,
        'description': str_or_val_lang,
        'thumbnail': uri_or_image_resource,

        # Rights and Licensing properties
        'attribution': str_or_val_lang,
        'logo': uri_or_image_resource,
        'license': repeatable_string,

        # Technical properties
        Required('@id'): http_uri,
        Required('@type'): 'sc:Manifest',
        'format': not_allowed,
        'height': not_allowed,
        'width': not_allowed,
        'viewingDirection': viewing_dir,
        'viewingHint': viewing_hint,

        # Linking properties
        'related': repeatable_uri,
        'service': service,
        'seeAlso': repeatable_string,
        'within': repeatable_uri,
        'startCanvas': not_allowed,
        Required('sequences'): manifest_sequence_list
    },
    extra=ALLOW_EXTRA
)


class ManifestValidator:
    """Does manifest validation.

    Will catch any exceptions during validation and store them.
    """
    def __init__(self):
        self._schema = ManifestSchema
        self.errors = None
        self.is_valid = None
        self.modified = None

    def validate(self, jdump, strict=False):
        """Validate a Manifest.

        :param jdump: Json dump of a IIIF2.0 Manifest
        :return: Any errors or None.
        """
        ret = None
        self.is_valid = False
        self.errors = None
        try:
            self.modified = ManifestSchema(jdump)
            self.is_valid = True
        except Exception as e:
            self.errors = str(e)
            self.is_valid = False

