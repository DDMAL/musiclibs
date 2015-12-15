import React, { PropTypes } from 'react';
import Im from 'immutable';
import { Link } from 'react-router';

import DescriptionList from '../ui/description-list';
import Description from './description';

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

/** Display a list of hits */
export function HitList({ hits })
{
    const terms = Im.Seq(hits)
        .filter(hit => hit.field !== 'metadata' && hit.field.indexOf('_') === -1)
        .map((hit, i) => ({
            term: hit.field.charAt(0).toUpperCase() + hit.field.slice(1),
            description: hit.parsed.map((text, i) => (
                i % 2 === 0 ? <span key={i}>{text}</span> : <mark key={i}>{text}</mark>
            ))
        }))
        .toArray();

    if (terms.length === 0)
        return <noscript />;

    return <DescriptionList style={{ marginLeft: 20 }} terms={terms} />;
}

HitList.propTypes = {
    hits: PropTypes.objectOf(Im.List)
};

export default SearchResultItem;
