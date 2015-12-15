import React, { PropTypes } from 'react';
import { Link } from 'react-router';

import Description from './description';
import HitList from './hit-list';

/** Display basic information for a search result, linking to the full manifest */
function SearchResultItem({ result })
{
    return (
        <div>
            <h2 className="h3"><Link to={`/manifests/${result.id}/`}>{result.label}</Link></h2>
            {result.description ? <Description text={result.description} /> : null}
            <HitList hits={result.hits} />
        </div>
    );
}

SearchResultItem.propTypes = {
    result: PropTypes.shape({
        id: PropTypes.string.isRequired,

        label: PropTypes.oneOfType([
            PropTypes.string,
            PropTypes.arrayOf(PropTypes.string)
        ]).isRequired
    })
};

export default SearchResultItem;
