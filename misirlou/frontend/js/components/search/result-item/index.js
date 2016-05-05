import React from 'react';

import './search-result-item.css';
import { resultType } from './types';
import Thumbnail from './thumbnail';
import Content from './content';


/** Display basic information for a search result, linking to the full manifest */
export default function SearchResultItem({ result })
{
    return (
        <div className="search-result__item">
            <Thumbnail src={result.thumbnail} />
            <Content result={result} />
        </div>
    );
}

SearchResultItem.propTypes = {
    result: resultType.isRequired
};

export const __hotReload = true;
