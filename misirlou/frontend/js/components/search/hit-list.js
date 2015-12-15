import React, { PropTypes } from 'react';
import Im from 'immutable';

import DescriptionList from '../ui/description-list';

/** Display a list of hits */
function HitList({ hits })
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

    return <DescriptionList style={{ marginLeft: 30 }} terms={terms} />;
}

HitList.propTypes = {
    hits: PropTypes.objectOf(Im.List)
};

export default HitList;
