import React, { PropTypes } from 'react';
import { Link } from 'react-router';

import { manifestSummaryType } from '../../../iiif-types';

import './search-result-item.css';
import Description from './description';
import ExternalHtml from '../../external-content/external-html';
import HitList from './hit-list';
import { getHostname } from '../../../api/utils';

/** Display basic information for a search result, linking to the full manifest */
export default function Content({ result, query, pitchQuery })
{
    let linkURL = `/manifests/${result['local_id']}`;

    if (query)
    {
        linkURL += `/?q=${query}`;
        linkURL += (pitchQuery) ? `&m=${pitchQuery}` : '';
    }

    let highlightedLabel = highlightLabel(result.label, result.hits);
    let parsedHits = result.hits;
    if (highlightedLabel !== result.label)
        parsedHits = result.hits.filter(hit => hit.field.indexOf('label') === -1);

    return (
        <div className="search-result__item__content">
            <h2 className="h4">
                <Link to={linkURL}>{highlightedLabel}</Link> <br/>
                <small>{getHostname(result['@id'])}</small>
            </h2>
            {result.description && <Description text={result.description} />}
            {/* FIXME(wabain): Do margin in CSS */}
            {result.attribution && (
                <dl style={{ marginBottom: 10 }}>
                    <dt>Source</dt>
                    <dd>
                        <ExternalHtml>{result.attribution}</ExternalHtml>
                    </dd>
                </dl>
            )}
            <HitList hits={parsedHits} />
        </div>
    );
}

Content.propTypes = {
    result: manifestSummaryType.isRequired,
    query: PropTypes.string,
    pitchQuery: PropTypes.string
};


// If a highlight on the label, return new label with highlighting.
function highlightLabel(label, hits)
{
    let parsed;
    for (const hit of hits.filter(hit => hit.field.indexOf('label') !== -1))
    {
        if (hit.field === 'label' || hit.field === 'label_txt_en')
        {
            parsed = hit.parsed.slice();
            break;
        }
        else if (!parsed)
        {
            parsed = hit.parsed.slice();
        }
    }
    if (!parsed)
        return label;

    const parsedSubstring = parsed.join('');
    const startIndex = label.indexOf(parsedSubstring);
    const prefix = label.slice(0, startIndex);
    const suffix  = label.slice(startIndex + parsedSubstring.length);
    parsed[0] = prefix + parsed[0];
    parsed[parsed.length - 1] = parsed[parsed.length - 1] + suffix;

    return parsed.map((text, i) => (
        i % 2 === 0 ? <span>{text}</span> : <span className="search-result__label-highlight">{text}</span>));
}
