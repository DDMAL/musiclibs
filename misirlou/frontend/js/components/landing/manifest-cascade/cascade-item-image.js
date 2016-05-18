import React from 'react';

import { getImageUrlWithMaxWidth } from '../../../utils/iiif-manifest-accessors';
import { getLinks } from '../../../utils/json-ld-accessors';

import { thumbnailType } from './types';
import './cascade-item.css';

const THUMBNAIL_MAX_WIDTH = 500;

export default function ManifestCascadeItemImage({ thumbnail })
{
    const src = getThumbnailImage(thumbnail);

    // FIXME(wabain): Could this really happen?
    if (!src)
        return <noscript />;

    const imageStyle = {
        backgroundImage: `url("${src}")`
    };

    return (
        <div className="manifest-cascade__item__background" style={imageStyle} />
    );
}

ManifestCascadeItemImage.propTypes = {
    thumbnail: thumbnailType
};

/**
 * @param thumbnail
 * @returns {?string}
 */
function getThumbnailImage(thumbnail)
{
    if (typeof thumbnail === 'string')
        return thumbnail;

    if (typeof thumbnail !== 'object' || thumbnail === null)
        return null;

    // FIXME(wabain): Can this happen?
    if (Array.isArray(thumbnail))
        return getThumbnailImage(thumbnail[0]);

    if (thumbnail.service)
    {
        const tailored = getImageUrlWithMaxWidth(thumbnail, THUMBNAIL_MAX_WIDTH);

        if (tailored)
            return tailored;
    }

    const ids = getLinks(thumbnail);

    if (ids.length < 1)
        return null;

    return ids[0];
}
