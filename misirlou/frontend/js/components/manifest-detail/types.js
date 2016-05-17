import { PropTypes } from 'react';

// Don't validate other properties via React
export const manifestShape = PropTypes.shape({
    '@context': PropTypes.oneOfType([PropTypes.string, PropTypes.array]).isRequired,
    '@id': PropTypes.string.isRequired
});
