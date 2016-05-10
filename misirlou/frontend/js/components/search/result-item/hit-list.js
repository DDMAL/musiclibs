import React, { PropTypes } from 'react';
import Im from 'immutable';

import DescriptionList from '../../ui/description-list';


const HIT_WITH_LANG = /(.*)_txt_(.*)/;


/** Display a list of hits */
export default function HitList({ hits })
{
    const terms = Im.Seq(hits)
        .filter(hit => hit.field.indexOf('metadata') === -1)
        .map(getTerm)
        .reduce(getPreferredLang, Im.Map())
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
    let lang = null;
    let field = hit.field;

    const langCoded = HIT_WITH_LANG.exec(field);

    if (langCoded)
    {
        field = langCoded[1];
        lang = langCoded[2];
    }

    const term = field.charAt(0).toUpperCase() + field.slice(1);
    const description = hit.parsed.map((text, i) => (
        i % 2 === 0 ? <span key={i}>{text}</span> : <mark key={i}>{text}</mark>
    ));

    return {
        term,
        lang,
        description
    };
}

function getPreferredLang(prefs, hit)
{
    if (hit.lang === 'en' || !prefs.has(hit.term))
        return prefs.set(hit.term, hit);

    return prefs.update(hit.term, prior =>
    {
        if (prior.lang === null || prior.lang === 'en')
            return prior;

        return hit;
    });
}

