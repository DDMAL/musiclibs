import React, { PropTypes } from 'react';
import { Link } from 'react-router';

import Description from './description';
import HitList from './hit-list';

/** Display basic information for a search result, linking to the full manifest */
function SearchResultItem({ result })
{
    const label = result.label.join(', ');

    return (
        <div>
            <h2 className="h3"><Link to={`/manifests/${result.id}/`}>{label}</Link></h2>
            {result.description.map((description, i) => (
                <Description key={i} text={description} />
            ))}
            <HitList hits={result.hits} />
        </div>
    );
}

SearchResultItem.propTypes = {
    result: PropTypes.shape({
        id: PropTypes.string.isRequired,

        label: PropTypes.arrayOf(PropTypes.string).isRequired,
        description: PropTypes.arrayOf(PropTypes.string).isRequired
    }).isRequired
};

export default SearchResultItem;

export const __hotReload = true;
