import React, { PropTypes } from 'react';
import { Link } from 'react-router';

import { manifestSummaryType } from '../../../iiif-types';

import './search-result-item.css';
import Description from './description';
import ExternalHtml from '../../external-content/external-html';
import HitList from './hit-list';


/** Display basic information for a search result, linking to the full manifest */
export default function Content({ result, query, pitchQuery })
{
    let linkURL = `/manifests/${result['local_id']}`;

    if (query)
    {
        linkURL += `/?q=${query}`;
        linkURL += (pitchQuery) ? `&m=${pitchQuery}` : '';
    }

    return (
        <div className="search-result__item__content">
            <h2 className="h4">
                <Link to={linkURL}>{result.label}</Link> <br/>
                <small>{getHostname(result['@id'])}</small>
            </h2>
            {result.description && <Description text={result.description} />}
            {/* FIXME(wabain): Do margin in CSS */}
            {result.attribution && (
                <dl style={{ marginBottom: 10 }}>q
                    <dt>Source</dt>
                    <dd>
                        <ExternalHtml>{result.attribution}</ExternalHtml>
                    </dd>
                </dl>
            )}
            <HitList hits={result.hits} />
        </div>
    );
}

Content.propTypes = {
    result: manifestSummaryType.isRequired,
    query: PropTypes.string,
    pitchQuery: PropTypes.string
};

// Return the host name out from a url.
function getHostname(url)
{
    /* global document */
    const parser = document.createElement('a');
    parser.href = url;
    return parser.hostname;
}
