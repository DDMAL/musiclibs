import { PropTypes } from 'react';

const { oneOfType, string, shape, number } = PropTypes;

export const thumbnailType = oneOfType([
    string,
    shape({
        width: number.isRequired,
        height: number.isRequired,
        service: shape({
            '@id': string.isRequired,
            'profile': string.isRequired
        }).isRequired
    })
]);

export const resultType = shape({
    id: PropTypes.string.isRequired,
    thumbnail: thumbnailType.isRequired,
    label: PropTypes.arrayOf(PropTypes.string).isRequired,
    description: PropTypes.arrayOf(PropTypes.string).isRequired
});
