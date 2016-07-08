import urllib.parse
import json
from voluptuous import Schema, Required, Invalid, MultipleInvalid, ALLOW_EXTRA


class ValidatorWarning:
    """Warning that can hold an in-document path and a message."""
    def __init__(self, msg, path):
        self.msg = msg
        self.path = path

    def __str__(self):
        path = ' @ data[%s]' % ']['.join(map(repr, self.path)) \
            if self.path else ''
        output = "Warning: {}".format(self.msg)
        return output + path

    def __repr__(self):
        return "ValidatorWarning('{}', {})".format(self.msg, self.path)

    def __lt__(self, other):
        return len(self.path) < len(other.path)

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return str(self) == str(other)


class ValidatorError(Invalid):
    """Subclass of Invalid with preferred behaviour to throw to voluptous."""

    def __str__(self):
        path = ' @ data[%s]' % ']['.join(map(repr, self.path)) \
            if self.path else ''
        output = "Error: {}".format(self.msg)
        return output + path

    def __repr__(self):
        return "ValidatorError('{}', {})".format(self.msg, self.path)

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return hash(str(self))

    def __lt__(self, other):
        return len(self.path) < len(other.path)


class BaseValidatorMixin:

    def __init__(self, iiif_validator=None):
        """You should NOT override ___init___. Override setup() instead."""
        self.raise_warnings = True
        self._errors = set()
        self.path = tuple()
        self.is_valid = None
        self.json = None
        self.corrected_doc = None
        self._IIIFValidator = iiif_validator
        self._LangValPairs = None

        self._LangValPairs = Schema(
            {
                Required('@language'): self.repeatable_string_type,
                Required('@value'): self.repeatable_string_type
            }
        )

        self.MetadataItemSchema = Schema(
            {
                'label': self.str_or_val_lang_type,
                'value': self.str_or_val_lang_type
            }
        )
        self.setup()

    def setup(self):
        """Do any other setup. Called at the end of __init__()"""
        pass

    @property
    def errors(self):
        errs = filter(lambda err: isinstance(err, ValidatorError), self._errors)
        return sorted(errs)

    @property
    def warnings(self):
        warns = filter(lambda warn: isinstance(warn, ValidatorWarning), self._errors)
        return sorted(warns)

    @property
    def ManifestValidator(self):
        return self._IIIFValidator._ManifestValidator

    @property
    def SequenceValidator(self):
        return self._IIIFValidator._SequenceValidator

    @property
    def CanvasValidator(self):
        return self._IIIFValidator._CanvasValidator

    @property
    def ImageResourceValidator(self):
        return self._IIIFValidator._ImageResourceValidator

    @ManifestValidator.setter
    def ManifestValidator(self, value):
        self._IIIFValidator._ManifestValidator = value(self._IIIFValidator)

    @SequenceValidator.setter
    def SequenceValidator(self, value):
        self._IIIFValidator._SequenceValidator = value(self._IIIFValidator)

    @CanvasValidator.setter
    def CanvasValidator(self, value):
        self._IIIFValidator._CanvasValidator = value(self._IIIFValidator)

    @ImageResourceValidator.setter
    def ImageResourceValidator(self, value):
        self._IIIFValidator._ImageResourceValidator = value(self._IIIFValidator)

    def print_errors(self):
        """Print the errors in a nice format."""
        for err in self.errors:
            print(err)

    def print_warnings(self):
        """Print the warnings in a nice format."""
        for warn in self.warnings:
            print(warn)

    def _reset(self, path):
        """Reset the validator to handle a new chunk of data."""
        self.json = None
        self.is_valid = None
        self._errors = set()
        self.path = path

    def _validate(self, json_dict, path=None, raise_warnings=None, **kwargs):
        """Public method to run validation."""
        if raise_warnings is not None:
            self.raise_warnings = raise_warnings

        # Reset the validator object constants.
        if not path:
            path = tuple()
        self._reset(path)

        # Load the json_dict argument as json if a raw string was provided.
        if isinstance(json_dict, str):
            json_dict = json.loads(json_dict)

        try:
            self.json = json_dict
            val = self._run_validation(**kwargs)
            val = self._check_common_fields(val, path)
            self._raise_additional_warnings(val)
            self.corrected_doc = self.modify_validation_return(val)
            self.is_valid = True
        except MultipleInvalid as e:
            # Cast all errors to comparable ones before returning.
            for err in e.errors:
                if isinstance(err, ValidatorWarning):
                    self._errors.add(err)
                elif isinstance(err, ValidatorError):
                    err.path = self.path + tuple(err.path)
                    self._errors.add(err)
                else:
                    err.path = self.path + tuple(err.path)
                    new_err = ValidatorError(err.msg, tuple(err.path))
                    self._errors.add(new_err)
        if self.errors:
            self.is_valid = False

    def _run_validation(self, **kwargs):
        """Do the actual action of validation. Called by validate()."""
        raise NotImplemented

    def _raise_additional_warnings(self, validation_results):
        """Inspect the block and raise any SHOULD warnings.

        This method is called only if the manifest validates without errors.
        It is passed the block that was just validated. This is the opportunity
        to inspect for fields which SHOULD be there and throw warnings.
        """
        raise NotImplemented

    def modify_validation_return(self, validation_results):
        """Do any final corrections or checks on a block before it is returned.

        This method is passed whatever value the validator is about to return to
        it's caller. Here you can check for missing keys, compare neighbours,
        make modifications or additions: anything you'd like to check or correct
        before return.

        :param validation_results: A dict representing a json object.
        :return (dict): The sole argument, with some modification applied to it.
        """
        return validation_results

    def _handle_warning(self, field, msg):
        """Add a warning to the validator if warnings are being caught.

        :param field: The field the warning was raised on.
        :param msg: The message to associate with the warning.
        """
        if self.raise_warnings:
            self._errors.add(ValidatorWarning(msg, self.path + (field,)))

    def _sub_validate(self, subschema, value, path, **kwargs):
        """Validate a field using another Validator.

        :param subschema: A BaseValidatorMixin implementing object.
        :param value (dict): The data to be validated.
        :param path (tuple): The path where the above data exists.
            Example: ('sequences', 'canvases') for the CanvasValidator.
        :param kwargs: Any keys to subschema._run_validation()
            - canvas_uri: String passed to ImageResourceValidator from
              CanvasValidator to ensure 'on' key is valid.
            - raise_warnings: bool to decide if warnings will be recorded
              or not.
        """
        subschema._validate(value, path, **kwargs)
        if subschema._errors:
            self._errors = self._errors | subschema._errors
        if subschema.corrected_doc:
            return subschema.corrected_doc
        else:
            return subschema.json

    def _check_common_fields(self, val, path):
        """Validate fields that could appear on any resource."""
        common_fields = Schema(
            {
                "label": self.repeatable_string_type,
                "metadata": self.metadata_field,
                "description:": self.str_or_val_lang_type,
                "thumbnail": self.thumbnail_field,
                "logo": self.logo_field,
                "attribution": self.repeatable_string_type,
                "license": self.repeatable_uri_type,
                Required("@type"): str,
                "related": self.repeatable_uri_type,
                "rendering": self.repeatable_uri_type,
                "service": self.repeatable_uri_type,
                "seeAlso": self.repeatable_uri_type,
                "within": self.repeatable_uri_type,
            }, extra=ALLOW_EXTRA
        )
        return common_fields(val)

    def _check_should_warnings(self, resource, r_dict, fields):
        """Raise warnings if fields which should be in r_dict are not.

        :param resource (str): The name of the resource represented by r_dict
        :param r_dict (dict): The dict that will have it's keys checked.
        :param fields (list): The keys to check for in r_dict.
        """
        for f in fields:
            if not r_dict.get(f):
                self._handle_warning(f, "{} SHOULD have {} field.".format(resource, f))

    # Field definitions #
    def optional(self, field, fn):
        """Wrap a function to make its value optional (null and '' allows)"""
        def new_fn(*args):
            if args[0] == "" or args[0] is None:
                self._handle_warning(field, "'{}' field should not be included if it is empty.".format(field))
                return args[0]
            return fn(*args)
        return new_fn

    def not_allowed(self, value):
        """Raise invalid as this key is not allowed in the context."""
        raise ValidatorError("Key is not allowed here.")

    def str_or_val_lang_type(self, value):
        """Check value is str or lang/val pairs, else raise ValidatorError.

        Allows for repeated strings as per 5.3.2.
        """
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            return [self.str_or_val_lang_type(val) for val in value]
        if isinstance(value, dict):
            return self._LangValPairs(value)
        raise ValidatorError("Str_or_val_lang: {}".format(value))

    def repeatable_string_type(self, value):
        """Allows for repeated strings as per 5.3.2."""
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            for val in value:
                if isinstance(val, dict):
                    return self._LangValPairs(val)
                if not isinstance(val, str):
                    raise ValidatorError("Overly nested strings: {}".format(value))
            return value
        raise ValidatorError("repeatable_string: {}".format(value))

    def repeatable_uri_type(self, value):
        """Allow single or repeating URIs.

        Based on 5.3.2 of Presentation API
        """
        if isinstance(value, list):
            return [self.uri_type(val) for val in value]
        else:
            return self.uri_type(value)

    def http_uri_type(self, value):
        """Allow single URI that MUST be http(s)

        Based on 5.3.2 of Presentation API
        """
        return self.uri_type(value, http=True)

    def uri_type(self, value, http=False):
        """Check value is URI type or raise ValidatorError.

        Allows for multiple URI representations, as per 5.3.1 of the
        Presentation API.
        """
        if isinstance(value, str):
            return self._string_uri(value, http)
        elif isinstance(value, dict):
            emb_uri = value.get('@id')
            if not emb_uri:
                raise ValidatorError("URI not found: {} ".format(value))
            return self._string_uri(emb_uri, http)
        else:
            raise ValidatorError("Can't parse URI: {}".format(value))

    def _string_uri(self, value, http=False):
        """Validate that value is a string that can be parsed as URI.

        This is the last stop on the recursive structure for URI checking.
        Should not actually be used in schema.
        """
        # Always raise invalid if the string field is not a string.
        if not isinstance(value, str):
            raise ValidatorError("URI is not String: '{]'".format(value))
        # Try to parse the url.
        try:
            pieces = urllib.parse.urlparse(value)
        except AttributeError as a:
            raise ValidatorError("URI is not valid: '{}'".format(value))
        if not all([pieces.scheme, pieces.netloc]):
            raise ValidatorError("URI is not valid: '{}'".format(value))
        if http and pieces.scheme not in ['http', 'https']:
            raise ValidatorError("URI must be http: '{}'".format(value))
        return value

    def metadata_field(self, value):
        """General type check for metadata.

        Recurse into keys/values and checks that they are properly formatted.
        """
        if isinstance(value, list):
            return [self.MetadataItemSchema(val) for val in value]
        raise ValidatorError("Metadata key MUST be a list.")

    def thumbnail_field(self, value):
        if isinstance(value, str):
            self._handle_warning("thumbnail", "Thumbnail SHOULD be IIIF image service.")
            return self.uri_type(value)
        if isinstance(value, dict):
            path = self.path + ("thumbnail",)
            if value.get("@type"):
                return self._sub_validate(self.ImageResourceValidator, value, path,
                                      only_resource=True, raise_warnings=self.raise_warnings)
            else:
                val = self.uri_type(value)
                self._handle_warning("thumbnail", "Thumbnail SHOULD be IIIF image service.")
                return val

    def logo_field(self, value):
        if isinstance(value, str):
            self._handle_warning("logo", "Logo SHOULD be IIIF image service.")
            return self.uri_type(value)
        if isinstance(value, dict):
            path = self.path + ("logo",)
            if value.get("@type"):
                return self._sub_validate(self.ImageResourceValidator, value, path,
                                      only_resource=True, raise_warnings=self.raise_warnings)
            else:
                val = self.uri_type(value)
                self._handle_warning("logo", "Logo SHOULD be IIIF image service.")
                return val


class IIIFValidator(BaseValidatorMixin):
    def __init__(self):
        super().__init__()
        self._IIIFValidator = self
        self._ManifestValidator = ManifestValidator(self)
        self._ImageResourceValidator = ImageResourceValidator(self)
        self._CanvasValidator = CanvasValidator(self)
        self._SequenceValidator = SequenceValidator(self)

    def _set_from_sub(self, sub):
        """Set the validation attributes to those of a sub_validator"""
        self.is_valid = sub.is_valid
        self._errors = sub._errors
        self.corrected_doc = sub.corrected_doc

    def validate_manifest(self, json_dict, **kwargs):
        self._sub_validate(self.ManifestValidator, json_dict, path=None, **kwargs)
        self._set_from_sub(self.ManifestValidator)


class ManifestValidator(BaseValidatorMixin):
    PRESENTATION_API_URI = "http://iiif.io/api/presentation/2/context.json"
    IMAGE_API_1 = "http://library.stanford.edu/iiif/image-api/1.1/context.json"
    IMAGE_API_2 = "http://iiif.io/api/image/2/context.json"

    VIEW_DIRS = ['left-to-right', 'right-to-left',
                 'top-to-bottom', 'bottom-to-top']
    VIEW_HINTS = ['individuals', 'paged', 'continuous']

    def __init__(self, iiif_validator):
        """You should not override ___init___. Override setup() instead."""
        super().__init__(iiif_validator)
        self.ManifestSchema = None
        self.MetadataItemSchema = None
        self.setup()

    def setup(self):

        # Schema for validating manifests with flexible corrections.
        self.ManifestSchema = Schema(
            {
                # Descriptive properties
                Required('label'): self.str_or_val_lang_type,
                '@context': self.presentation_context_field,
                'metadata': self.metadata_field,

                'description': self.str_or_val_lang_type,

                # Technical properties
                Required('@id'): self.http_uri_type,
                Required('@type'): 'sc:Manifest',
                'format': self.not_allowed,
                'height': self.not_allowed,
                'width': self.not_allowed,
                'startCanvas': self.not_allowed,
                'viewingDirection': self.viewing_dir,
                'viewingHint': self.viewing_hint,

                Required('sequences'): self.sequences_field
            },
            extra=ALLOW_EXTRA
        )
        self.MetadataItemSchema = Schema(
            {
                'label': self.str_or_val_lang_type,
                'value': self.str_or_val_lang_type
            }
        )

    def _run_validation(self, **kwargs):
        return self.ManifestSchema(self.json)

    def _raise_additional_warnings(self, validation_results):
        self._check_should_warnings("manifest", validation_results, ["metadata", "description", "thumbnail"])

    def presentation_context_field(self, value):
        if isinstance(value, str):
            if not value == self.PRESENTATION_API_URI:
                raise ValidatorError("'@context' must be set to '{}'".format(self.PRESENTATION_API_URI))
        if isinstance(value, list):
            if self.PRESENTATION_API_URI not in value:
                raise ValidatorError("'@context' must be set to '{}'".format(self.PRESENTATION_API_URI))
        return value

    def metadata_field(self, value):
        """General type check for metadata.

        Recurse into keys/values and checks that they are properly formatted.
        """
        if isinstance(value, list):
            return [self.MetadataItemSchema(val) for val in value]
        raise ValidatorError("Metadata key MUST be a list.")

    def viewing_dir(self, value):
        """Validate against VIEW_DIRS list."""
        if value not in self.VIEW_DIRS:
            raise ValidatorError("viewingDirection: {}".format(value))
        return value

    def viewing_hint(self, value):
        """Validate against VIEW_HINTS list."""
        if value not in self.VIEW_HINTS:
            raise ValidatorError("viewingHint: {}".format(value))
        return value

    def sequences_field(self, value):
        """Validate sequence list for Manifest.

        Checks that exactly 1 sequence is embedded.
        """
        path = self.path + ("sequences", )
        if not isinstance(value, list):
            raise ValidatorError("'sequences' must be a list.")
        lst = [self._sub_validate(self.SequenceValidator, value[0], path,
                                  raise_warnings=self.raise_warnings, emb=True)]
        lst.extend([self._sub_validate(self.SequenceValidator, value[s], path,
                                  raise_warnings=self.raise_warnings, emb=False) for s in lst[1:] ])
        return lst


class SequenceValidator(BaseValidatorMixin):
    VIEW_DIRS = {'left-to-right', 'right-to-left',
                 'top-to-bottom', 'bottom-to-top'}
    VIEW_HINTS = {'individuals', 'paged', 'continuous'}

    def __init__(self, iiif_validator):
        """You should not override ___init___. Override setup() instead."""
        super().__init__(iiif_validator)
        self.EmbSequenceSchema = None
        self.LinkedSequenceSchema = None
        self.setup()

    def setup(self):

        # An embedded sequence must contain canvases.
        self.EmbSequenceSchema = Schema(
            {
                Required('@type'): 'sc:Sequence',
                '@context': self.not_allowed,
                '@id': self.http_uri_type,
                'label': self.str_or_val_lang_type,
                'startCanvas': self.uri_type,
                Required('canvases'): self.canvases_field,
                'viewingDirection': self.viewing_direction_field,
                'viewingHint': self.viewing_hint_field
            },
            extra=ALLOW_EXTRA
        )

        # A linked sequence must have an @id and no canvases
        self.LinkedSequenceSchema = Schema(
            {
                Required('@type'): 'sc:Sequence',
                Required('@id'): self.http_uri_type,
                'canvases': self.not_allowed
            },
            extra=ALLOW_EXTRA
        )

    def _run_validation(self, **kwargs):
        return self._validate_sequence(**kwargs)

    def _validate_sequence(self, emb=True):
        value = self.json
        if emb:
            return self.EmbSequenceSchema(value)
        else:
            return self.LinkedSequenceSchema(value)

    def _raise_additional_warnings(self, validation_results):
        pass

    def canvases_field(self, value):
        """Validate canvas list for Sequence."""
        if not isinstance(value, list):
            raise ValidatorError("'canvases' MUST be a list.")
        if len(value) < 1:
            raise ValidatorError("'canvases' MUST have at least one entry.")
        path = self.path + ("canvases", )
        return [self._sub_validate(self.CanvasValidator, c, path,
                                   raise_warnings=self.raise_warnings) for c in value]

    def viewing_hint_field(self, value):
        if value not in self.VIEW_HINTS:
            try:
                return self.uri_type(value)
            except Invalid:
                raise ValidatorError("Viewing hint is not known and not uri.")
        return value

    def viewing_direction_field(self, value):
        if value not in self.VIEW_DIRS:
            raise Invalid("Unknown viewingDirection.")
        return value


class CanvasValidator(BaseValidatorMixin):
    VIEW_HINTS = {'non-paged', 'facing-pages'}

    def __init__(self, iiif_validator):
        """You should not override ___init___. Override setup() instead."""
        super().__init__(iiif_validator)
        self.CanvasSchema = None
        self.setup()

    def setup(self):
        self.CanvasSchema = Schema(
            {
                Required('@id'): self.http_uri_type,
                Required('@type'): 'sc:Canvas',
                Required('label'): self.str_or_val_lang_type,
                Required('height'): int,
                Required('width'): int,
                'viewingHint': self.viewing_hint_field,
                'images': self.images_field,
                'other_content': self.other_content_field
            },
            extra=ALLOW_EXTRA
        )

    def _run_validation(self, **kwargs):
        self.canvas_uri = self.json['@id']
        return self.CanvasSchema(self.json)

    def _raise_additional_warnings(self, validation_results):
        self._check_should_warnings("canvas", validation_results, ["thumbnail"])

    def images_field(self, value):
        if isinstance(value, list):
            path = self.path + ("images",)
            return [self._sub_validate(self.ImageResourceValidator, i, path,
                                       canvas_uri=self.canvas_uri,
                                       raise_warnings=self.raise_warnings) for i in value]
        if not value:
            return
        raise ValidatorError("'images' must be a list")

    def other_content_field(self, value):
        if not isinstance(value, list):
            raise ValidatorError("otherContent must be list!")
        return [self.uri_type(item['@id']) for item in value]

    def viewing_hint_field(self, value):
        if value not in self.VIEW_HINTS:
            try:
                return self.uri_type(value)
            except Invalid:
                raise ValidatorError("Viewing hint is not known and not uri.")


class ImageResourceValidator(BaseValidatorMixin):

    def __init__(self, iiif_validator):
        """You should not override ___init___. Override setup() instead."""
        super().__init__(iiif_validator)
        self.ImageSchema = None
        self.ImageResourceSchema = None
        self.ServiceSchema = None
        self.canvas_uri = None
        self.setup()

    def setup(self):
        self.ImageSchema = Schema(
            {
                "@id": self.id_field,
                Required('@type'): "oa:Annotation",
                Required('motivation'): "sc:painting",
                Required('resource'): self.image_resource_field,
                Required("on"): self.on_field
            }, extra=ALLOW_EXTRA
        )
        self.ImageResourceSchema = Schema(
            {
                Required('@id'): self.http_uri_type,
                '@type': self.resource_type_field,
                "service": self.image_service_field
            }, extra=ALLOW_EXTRA
        )

        self.ServiceSchema = Schema(
            {
                '@context': self.repeatable_uri_type,
                '@id': self.uri_type,
                'profile': self.service_profile_field,
                'label': str
            }, extra=ALLOW_EXTRA
        )

    def _run_validation(self, canvas_uri=None, only_resource=False, **kwargs):
        self.canvas_uri = canvas_uri
        if only_resource:
            return self.ImageResourceSchema(self.json)
        else:
            return self.ImageSchema(self.json)

    def _raise_additional_warnings(self, validation_results):
        self._check_should_warnings("Annotation", validation_results, ["@id"])

    def id_field(self, value):
        """Validate the @id property of an Annotation."""
        try:
            return self.http_uri_type(value)
        except Invalid:
            self._handle_warning("@id", "Field SHOULD be http.")
            return self.uri_type(value)

    def on_field(self, value):
        """Validate the 'on' property of an Annotation."""
        if value != self.canvas_uri:
            raise ValidatorError("'on' must reference the canvas URI.")
        return value

    def resource_type_field(self, value):
        """Validate the '@type' field of an Image Resource."""
        if value != 'dctypes:Image':
            self._handle_warning("@type", "'@type' field SHOULD be 'dctypes:Image'")
        return value

    def image_resource_field(self, value):
        """Validate image resources inside images list of Canvas"""
        if value.get('@type') == 'oa:Choice':
            return self.ImageResourceSchema(value['default'])
        return self.ImageResourceSchema(value)

    def image_service_field(self, value):
        """Validate against Service sub-schema."""
        if isinstance(value, str):
            return self.uri_type(value)
        elif isinstance(value, list):
            return [self.image_service_field(val) for val in value]
        else:
            return self.ServiceSchema(value)

    def service_profile_field(self, value):
        """Profiles in services are a special case.

        The profile key can contain a uri, or a list with extra
        metadata and a uri in the first position.
        """
        if isinstance(value, list):
            return self.uri_type(value[0])
        else:
            return self.uri_type(value)


def get_schema(uri):
    """Configure a schemas based on settings relevant to given uri."""
    import misirlou.helpers.manifest_utils.library_specific_exceptions as libraries

    parsed = urllib.parse.urlparse(uri)
    netloc = parsed.netloc

    if netloc == "iiif.lib.harvard.edu":
        return libraries.get_harvard_edu_validator()
    if netloc == "digi.vatlib.it":
        return libraries.get_vatlib_it_validator()
    if netloc == "purl.stanford.edu":
        return libraries.get_stanford_edu_validator()
    if netloc == "iiif.archivelab.org":
        return libraries.get_archivelab_org_validator()
    if netloc == "gallica.bnf.fr":
        return libraries.get_gallica_bnf_fr_validator()

    return libraries.FlexibleValidator()
