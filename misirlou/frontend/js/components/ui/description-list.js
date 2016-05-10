import Im from 'immutable';
import React, { PropTypes } from 'react';

/**
 * Given an array of objects in the form {term, description},
 * return a description list for those terms.
 */
export default function DescriptionList({ terms, ...etc })
{
    const listing = Im.Seq(terms).map(({ term, description }, i) => [
        <dt key={`t-${i}`}>{term}</dt>,
        <dd key={`d-${i}`}>{description}</dd>
    ])
    .flatten(true)
    .toArray();

    return <dl {...etc}>{listing}</dl>;
}

DescriptionList.propTypes = {
    terms: PropTypes.arrayOf(PropTypes.shape({
        term: PropTypes.any.isRequired,
        description: PropTypes.any.isRequired
    })).isRequired
};
