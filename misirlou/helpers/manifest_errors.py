class ErrorMap:
    """Provide map for error messages between human readable and int repr."""

    # Map of errors indexed by ints and string names.
    _error_map = {
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
        11: ("FAILED_IMAGE_REQUEST", "Could not retrieve an image from manifest.")
    }

    _error_map.update({(c, (i, m)) for (i, (c, m)) in _error_map.items()})

    def __getitem__(self, item):
        if isinstance(item, str):
            name = item
            code, msg = self._error_map[item]
        elif isinstance(item, int):
            code = item
            name, msg = self._error_map[item]
        else:
            raise ValueError("Expected string or int.")
        return ManifestError(code, name, msg)


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
