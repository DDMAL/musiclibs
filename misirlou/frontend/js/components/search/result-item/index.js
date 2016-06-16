import React, { PropTypes } from 'react';

import './search-result-item.css';
import { manifestSummaryType } from '../../../iiif-types';
import Thumbnail from './thumbnail';
import Content from './content';


/** Display basic information for a search result, linking to the full manifest */
export default function SearchResultItem({ result, query, pitchQuery })
{
    return (
        <div className="search-result__item">
            <Thumbnail src={result.thumbnail} />
            <Content result={result} query={query} pitchQuery={pitchQuery} />
        </div>
    );
}

SearchResultItem.propTypes = {
    result: manifestSummaryType.isRequired,
    query: PropTypes.string
};

