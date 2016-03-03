from voluptuous import Schema, Required, Invalid, ALLOW_EXTRA
import urllib.parse
import json
import IPython

VIEW_DIRS = ['left-to-right', 'right-to-left',
             'top-to-bottom', 'bottom-to-top']
VIEW_HINTS = ['individuals', 'paged', 'continuous']


def not_allowed(value):
    """Raise invalid as this key is not allowed in the context."""
    raise Invalid("Key is not allowed here.")


def str_or_val_lang(value):
    """Check value is str or lang/val pairs, else raise Invalid.

    Allows for repeated strings as per 5.3.2.
    """
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        for val in value:
            str_or_val_lang(val)
        return value
    if isinstance(value, dict):
        lang_val_pairs(value)
        return value
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
    """Check value is Metadata type or raise Invalid."""
    if isinstance(value, list):
        for val in value:
            metadata_item(val)
        return value
    raise Invalid("Metadata is malformed.")


"""URI checking that allows for dicts and lists"""
"""============================================"""


def repeatable_uri(value):
    """Allow single or repeating URIs.

    Based on 5.3.2 of Presentation API
    """
    if isinstance(value, list):
        for val in value:
            uri(val)
    else:
        uri(value)

    return value


def http_uri(value):
    """Allow single URI that MUST be http(s)

    Based on 5.3.2 of Presentation API
    """
    uri(value, http=True)
    return value


def uri(value, http=False):
    """Check value is URI type or raise Invalid.

    Based on 5.3.1 of Presentation API
    """
    if isinstance(value, str):
        return string_uri(value, http)
    elif isinstance(value, dict):
        emb_uri = value.get('@id')
        if not emb_uri:
            raise Invalid("URI not found: {} ".format(value))
        return string_uri(emb_uri, http)
    else:
        raise Invalid("Can't parse URI: {}".format(value))


def string_uri(value, http=False):
    """Actual URI checking at the end of recursive structures."""
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


def uri_or_image_resource(value):
    """Check value is URI or image_resource or raise Invalid"""
    try:
        repeatable_uri(value)
    except Invalid:
        image_resource(value)
    return value


def service(value):
    """Validate against Service sub-schema."""
    return service_sub(value)


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


def image_resource(value):
    """Raise Invalid if not IIIFImageResource."""
    pass #not yet implemented


def manifest_sequence_list(value):
    """Validate sequence list for Manifest.

    Checks that exactly 1 sequence is embedded.
    """
    if not isinstance(value, list):
        raise Invalid("'sequences' must be a list")
    EmbSequenceSchema(value[0])
    for s in value[1:]:
        LinkedSequenceSchema(s)
    return value


def sequence_canvas_list(value):
    """Validate canvas list for Sequence."""
    if not isinstance(value, list):
        raise Invalid("'canvases' must be a list")
    for c in value:
        CanvasSchema(c)
    return value


def images_in_canvas(value):
    """Validate images list for Canvas"""
    if not isinstance(value, list):
        raise Invalid("'images' must be a list")
    for i in value:
        ImageSchema(i)
    return value

"""Sub-schema for lang-val pairs which can stand in for some stings.
   as defined in 5.3.3."""
lang_val_pairs = Schema(
    {
        '@language': repeatable_string,
        '@value': repeatable_string
    }
)

"""Sub-schema for items in the metadata list."""
metadata_item = Schema(
    {
        'label': str_or_val_lang,
        'value': str_or_val_lang
    }
)

"""Sub-schema for services."""
service_sub = Schema(
    {
        Required('@context'): uri,
        '@id': uri,
        'profile': uri,
        'label': str
    },
    extra=ALLOW_EXTRA
)


# Schema for Images
ImageSchema = Schema(
    {
        "@id": http_uri,
        Required('@type'): "oa:Annotation",
        Required('motivation'): "sc:painting",
        Required('resource'):
            {
                Required("@id"): http_uri,
                "@type": "dctypes:Image",
                "service": service
            },
        Required("on"): http_uri
    }, extra=ALLOW_EXTRA
)

# Schema for Canvases.
CanvasSchema = Schema(
    {
        Required('@id'): http_uri,
        Required('@type'): 'sc:Canvas',
        Required('label'): str_or_val_lang,
        Required('height'): int,
        Required('width'): int,
        Required('images'): images_in_canvas
    },
    extra=ALLOW_EXTRA
)

# An embedded sequence must contain canvases.
EmbSequenceSchema = Schema(
    {
        Required('@type'): 'sc:Sequence',
        '@id': http_uri,
        'label': str_or_val_lang,
        Required('canvases'): sequence_canvas_list
    },
    extra=ALLOW_EXTRA
)

# A linked sequence must have an @id and no canvases
LinkedSequenceSchema = Schema(
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
        'license': repeatable_uri,

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
        'seeAlso': repeatable_uri,
        'within': repeatable_uri,
        'startCanvas': not_allowed,
        Required('sequences'): manifest_sequence_list
    },
)


if __name__ == '__main__':
    with open('manifest.json') as f:
        man = json.load(f)
    IPython.embed()
