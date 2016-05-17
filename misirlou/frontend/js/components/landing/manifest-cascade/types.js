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
        'profile': string.isRequired
    })
});

export const thumbnailType = oneOfType([string, thumbnailShape]);

export const manifestSummaryType = shape({
    '@id': string.isRequired,
    'local_id': string.isRequired,

    'hits': array.isRequired,

    // FIXME(wabain): Check types, required here
    'label': string.isRequired,
    'thumbnail': thumbnailType.isRequired,
    'attribution': string,
    'description': string,
    'logo': string
});
