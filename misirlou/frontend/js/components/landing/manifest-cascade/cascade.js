import React, { PropTypes } from 'react';
import Im from 'immutable';

import { getImageUrlWithMaxWidth } from '../../../utils/iiif-manifest-accessors';
import { getLinks } from '../../../utils/json-ld-accessors';

import ManifestCascadeItem from './cascade-item';


const THUMBNAIL_MAX_WIDTH = 500;


/** Display a cascade of manifests */
export default function ManifestCascade({ columns: columnCount, manifestSummaries })
{
    const columnClass = `col-xs-${(12 / columnCount) | 0}`;

    const manifestInfo = manifestSummaries.map(manifestSummary =>
    {
        let img;

        if (manifestSummary.thumbnail)
            img = getThumbnail(manifestSummary.thumbnail);
        else
            img = null;

        return {
            manifestSummary,
            img
        };
    });

    let columnContents;

    if (columnCount === 1)
        // FIXME(wabain): Do I need flatten here?
        columnContents = [manifestInfo.flatten(true).toArray()];
    else
        columnContents = getColumnArray(columnCount, manifestInfo);

    return (
        <div className="row">
            {columnContents.map((content, i) => (
                <div key={i} className={columnClass}>
                    {content.map((info, j) => (
                        <ManifestCascadeItem key={j} {...info} />
                    ))}
                </div>
            ))}
        </div>
    );
}

ManifestCascade.propTypes = {
    columns: PropTypes.number.isRequired,
    // FIXME(wabain): Given smarter type here
    manifestSummaries: PropTypes.instanceOf(Im.List).isRequired
};

/**
 * Split manifest info into the given number of columns.
 *
 * @param columnCount
 * @param {Array<T>} manifestInfo
 * @returns {Array<Array<T>>} Columns
 */
function getColumnArray(columnCount, manifestInfo)
{
    const columns = Im.Repeat(Im.List(), columnCount).toJS();

    manifestInfo.forEach((info, index) => columns[index % columnCount].push(info));

    return columns;
}

/**
 * @param thumbnail
 * @returns {?string}
 */
function getThumbnail(thumbnail)
{
    if (typeof thumbnail === 'string')
        return thumbnail;

    if (typeof thumbnail !== 'object' || thumbnail === null)
        return null;

    // FIXME(wabain): Can this happen?
    if (Array.isArray(thumbnail))
        return getThumbnail(thumbnail[0]);

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
