class ErrorMap:
    """Provide map for error messages between human readable and int repr."""

    # Map of errors indexed by ints and string names.
    _error_map = {
        0: ("NO_ERROR", "No errors reported."),
        1: ("NO_DB_RECORD", "No database entry with this pk."),
        2: ("SOLR_RECORD_ERROR", "Could not resolve this pk in solr."),
        3: ("TIMEOUT_REMOTE_RETRIEVAL", "Timeout retrieving remote_manifest."),
        4: ("FAILED_REMOTE_RETRIEVAL", "Failed to retrieve manifest."),
        5: ("HTTPS_STORED", "Manifest: stored remote url is not https."),
        6: ("MANIFEST_SSL_FAILURE", "Manifest: SSL certificate verification failed."),
        7: ("HASH_MISMATCH", "Local manifest hash DNE remote manifest contents."),
        8: ("NO_THUMBNAIL", "Indexed document has no thumbnail."),
        9: ("IRRETRIEVABLE_THUMBNAIL", "Could not retrieve indexed thumbnail."),
        10: ("NON_IIIF_THUMBNAIL", "Stored thumbnail is not IIIF."),
        11: ("FAILED_IMAGE_REQUEST", "Could not retrieve an image from manifest."),
        12: ("NON_IIIF_IMAGE_IN_SEQUENCE", "Randomly selected image failed IIIF spec.")
    }

    # Index the above by the ALL_CAPS string representation as well.
    _error_map.update({(short_str, (i, msg))
                       for (i, (short_str, msg)) in _error_map.items()})

    def __getitem__(self, item):
        """Returns a 3-tuple of type (int_code, SHORT_STR, String message).

        The point of ErrorMap is to be able to refer to errors either as
        an integer or as a SHORT_STRING. This method provides that functionality.
        """
        if isinstance(item, str):
            name = item
            code, msg = self._error_map[item]
        elif isinstance(item, int):
            code = item
            name, msg = self._error_map[item]
        else:
            raise ValueError("Expected string or int.")
        return ManifestError(code, name, msg)

    def values(self):
        """Return a generator of all errors values.

        This method closely resembles the values() method that dicts have, only
        it does some trickiness to hide the duplication in the internal dict.
        """
        int_keys = (k for k in self._error_map.keys() if isinstance(k, int))
        for i in int_keys:
            name, msg = self._error_map[i]
            yield i, name, msg
        raise StopIteration

class ManifestError:
    """Container for manifest errors returned by ErrorMap."""

    def __init__(self, code, name, msg):
        self.code = code
        self.name = name
        self.msg = msg

    def __iter__(self):
        return iter((self.code, self.name, self.msg))

    def __repr__(self):
        msg = "ManifestError({}, {}, {})"
        return msg.format(*iter(self))

    def __str__(self):
        msg = "{} - {}: {}"
        return msg.format(*iter(self))

    def __int__(self):
        return int(self.code)

    def __hash__(self):
        return hash(self.code)

    def __eq__(self, other):
        return self.code == int(other)
