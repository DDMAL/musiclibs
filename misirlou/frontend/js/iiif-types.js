import { PropTypes } from 'react';

const { shape, string, number, array, oneOfType } = PropTypes;

const thumbnailShape = shape({
    '@id': string.isRequired,
    '@type': string.isRequired,
    'format': string.isRequired,
    'height': number.isRequired,
    'width': number.isRequired,

    // Optional
    'service': shape({
        '@id': string.isRequired,
        '@context': string.isRequired,

        // Optional
        'profile': string
    })
});

/** Allowed type of thumbnails (normalized on Musiclibs import) */
export const thumbnailType = oneOfType([string, thumbnailShape]);

/**
 * Allowed types for manifest summary info, as used for search results
 * and recent manifests list (normalized on Musiclibs import)
 */
export const manifestSummaryType = shape({
    '@id': string.isRequired,
    'local_id': string.isRequired,

    'hits': array.isRequired,

    'label': string.isRequired,
    'thumbnail': thumbnailType.isRequired,
    'attribution': string,
    'description': string,
    'logo': string
});
