##Introduction
The main goal of this project is to provide a validator for the IIIF presentation API 2.1 that is useful to both implementors and aggregators. That is, it should be provide complete and informative errors and warnings, be easy to set up and integrate into a larger system, and 

The manifest validator has been split up into a number of sub-validators, with the hope that it will be easy to reason about and extend in the future. 

This validator should catch all typing and value errors, and should raise warnings for most of the SHOULD directives in the API (there are a lot of these, so I will happily accept pull requests that add ones I missed).

## Basic Use
To validate a IIIF manifest, create a `IIIFValidator` object and pass a complete manifest as json text or dict to its `validate()` method. After validation has run, you can check the `is_valid` property for results, a well as the `errors` and `warnings` properties.
```python
>>> import requests
>>> from iiif_validator import IIIFValidator

>>> man = requests.get('https://images.simssa.ca/iiif/manuscripts/cdn-hsmu-m2149l4/manifest.json')
>>> iv = IIIFValidator()
>>> iv.validate_manifest(man.text)
>>> iv.is_valid
True
>>> iv.errors
[]
```

All known errors and warnings include the path where the error or warning was hit, which should make addressing the bug simpler.
```python
>>> man = # Some poorly formatted manifest.
>>> iv.validate_manifest(man)
>>> iv.print_errors()
Error: '@context' must be set to 'http://iiif.io/api/presentation/2/context.json' @ data['@context']
Error: expected int @ data['sequences']['canvases']['height']
Error: expected int @ data['sequences']['canvases']['width']
>>> iv.print_warnings()
Warning: '@type' field SHOULD be 'dctypes:Image' @ data['sequences']['canvases']['images']['@type']
```

 
## Customization/Correction
The validator is designed to make over-riding specific behaviour relatively straightforward. This is useful if you wish to use the validator in an aggregation service (as we do at [musiclibs.net](https://musiclibs.net)) and need to catch particular errors or enforce corrections on an external manifest before indexing/storing its content. This project relies heavily on the voluptuous validator. Reference the [voluptuous documentation](https://pypi.python.org/pypi/voluptuous) for a more detailed explanation of what voluptuous can do.

The validator is composed of multiple independent sub validators. The currently included validators are `ManifestValidator`, `SequenceValidator`, `CanvasValidator` and `ImageResourceValidator`. The top level validator (`IIIFValidator`) is only responsible for storing references to validators, calling the correct validator, and storing its results. In order to customize the behaviour of validation, you need only to sub-class one of the validators, then pass the newly modified class into the `IIIFValidator`. Below is an example from our own system.

```python
# We know that all manifests from library X have a systematic
# error in their manifests: they have incorrectly coppied the @context
# at the top level of their manifests. We can write a method to return
# a validator which can handle this situation, and include a warning
# that we sidestepped normal rules.

from iiif_validator import IIIFValidator, ManifestValidator

def get_library_X_validator():
    
    class PatchedManifestValidator(ManifestValidator): 
        # Ignore the incorrect context 
        def presentation_context_field(self, value):
            if value == 'http://iiif.io/api/presentation/2/context.j': # missing 'son'
                self._handle_warning("@context", "Applied library specific corrections. "
                                                 "Ignored sloppily coppied presentation context.")
            else:
                return super().presentation_context_field(self, value)
            return value
            
    iv = IIIFValidator()
    iv.ManifestValidator = PatchedManifestValidator
    return iv
```

In broad strokes, each validator works by declaring one or more voluptuous schemas and providing a set of validation functions to be used by these schema. This is why, in the above examples, we over-rode the `presentation_context_field()` method of the `ManifestValidator` class: this is the method used by the schema to validate the field in question. We can inspect the schemas directly to get an idea of which methods are used in validation (I've cleaned up and organized this output):
```python
>>> from iiif_validator import IIIFValidator

>>> iv = IIIFValidator()
>>> mv = IIIFValidator.ManifestValidator
>>> mv.ManifestSchema
<Schema({
    '@id': <bound method BaseValidatorMixin._http_uri_type>,
    '@type': 'sc:Manifest', 
    '@context': <bound method ManifestValidator._presentation_context_field>, 
    'label': <bound method BaseValidatorMixin._str_or_val_lang_type>,
    'description': <bound method BaseValidatorMixin._str_or_val_lang_type>,
    'metadata': <bound method ManifestValidator._metadata_field>,
    'sequences': <bound method ManifestValidator._sequences_field>}, 
    'viewingHint': <bound method ManifestValidator._viewing_hint_field>, 
    'viewingDirection': <bound method ManifestValidator._viewing_dir_field>, 
    'height': <bound method BaseValidatorMixin._not_allowed>,
    'width': <bound method BaseValidatorMixin._not_allowed>, 
    'startCanvas': <bound method BaseValidatorMixin._not_allowed>, 
    'format': <bound method BaseValidatorMixin._not_allowed>,
extra=ALLOW_EXTRA, required=False) object at 0x7f4c78056c50>
```

Over riding any of the functions referenced by this schema will change the behaviour of the validator. You may also supply a new voluptuous schema to the object if the given is insufficient. You can use this power to ignore errors you don't care about, add extra warnings to the validator, or even make corrections.

The voluptuous library also allows us to make corrections as we validate. Once again, I recommend you read the voluptuous documentation for a more thorough idea of how this all works. The gist is that any function used to validate a field (such as the `presentation_context_field` method we have seen) can either raise an exception (to mark the field as invalid), or return a value. The value can be anything you like. If the document is valid, then the returned fields are combined into a corrected version of the document. This document will be stored under the `corrected_document` key of the `IIIFValidator`. 

Applying your own corrections will take some diving into the source of this library, and a pretty decent understanding of the voluptuous library. As a motivating example, here is how we coerce strings to ints on the height and width fields of canvases (a surprisingly popular error).

```python
# Define a new CanvasValidator for use in a IIIFValidator.
# Can coerce strings to ints.

class FlexibleCanvasValidator(Canvasvalidator):
    def _setup(self):
        super()._setup()
        
        # New schema which has flexible behaviour for height and width.
        self.CanvasSchema = Schema(
            {
                Required('@id'): self._http_uri_type,
                Required('@type'): 'sc:Canvas',
                Required('label'): self._str_or_val_lang_type,
                Required('height'): self.str_or_int_type, #  instead of int
                Required('width'): self.str_or_int_type,  #  instead of int
                'images': self._images_field,
                'other_content': self._other_content_field
            },
            extra=ALLOW_EXTRA
        )
     
    def str_or_int_type(self, value):
        """Coerce strings to ints."""
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


class FlexibleValidator(IIIFValidator):
    def __init__(self):
        super().__init__()
        self.CanvasValidator = FlexibleCanvasValidator

```

If you are running an aggregation service, this is the general pattern you could use to make the validator as flexible as you need. If you simply do not use any number of the keys, just re-declare the schema of the relevant validator to exclude them. 