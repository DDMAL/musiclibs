import React from 'react';
import { Link } from 'react-router';

import { resultType } from './types';
import './search-result-item.css';
import Description from './description';
import HitList from './hit-list';


/** Display basic information for a search result, linking to the full manifest */
export default function Content({ result })
{
    const label = result.label.join(', ');

    return (
        <div className="search-result__item__content">
            <h2 className="h4"><Link to={`/manifests/${result.id}/`}>{label}</Link></h2>
            {result.description.map((description, i) => (
                <Description key={i} text={description} />
            ))}
            <HitList hits={result.hits} />
        </div>
    );
}

Content.propTypes = {
    result: resultType.isRequired
};

