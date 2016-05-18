import React, { PropTypes } from 'react';
import Im from 'immutable';

import ManifestCascadeItem from './cascade-item';


/** Display a cascade of manifests */
export default function ManifestCascade({ columns: columnCount, manifestSummaries })
{
    const columnClass = `col-xs-${(12 / columnCount) | 0}`;

    let columnContents;

    if (columnCount === 1)
        // FIXME(wabain): Do I need flatten here?
        columnContents = [manifestSummaries.flatten(true).toArray()];
    else
        columnContents = getColumnArray(columnCount, manifestSummaries);

    return (
        <div className="row">
            {columnContents.map((content, i) => (
                <div key={i} className={columnClass}>
                    {content.map((summary, j) => (
                        <ManifestCascadeItem key={j} manifestSummary={summary} />
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
