import React, { PropTypes } from 'react';
import Im from 'immutable';

import DescriptionList from '../../ui/description-list';


/** Display a list of hits */
export default function HitList({ hits })
{
    const terms = Im.Seq(hits)
        .filter(hit => hit.field !== 'metadata' && hit.field.indexOf('_') === -1)
        .map(getTerm)
        .toArray();

    if (terms.length === 0)
        return <noscript />;

    return <DescriptionList terms={terms} />;
}

HitList.propTypes = {
    hits: PropTypes.objectOf(Im.List)
};

/** Translate a hit into a user-friendly term for display */
function getTerm(hit)
{
    const term = hit.field.charAt(0).toUpperCase() + hit.field.slice(1);
    const description = hit.parsed.map((text, i) => (
        i % 2 === 0 ? <span key={i}>{text}</span> : <mark key={i}>{text}</mark>
    ));

    return {
        term,
        description
    };
}

export const __hotReload = true;
