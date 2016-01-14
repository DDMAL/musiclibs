import React, { PropTypes } from 'react';
import Im from 'immutable';

import ManifestCascadeItem, { PLACEHOLDER_MANIFEST_HEIGHT } from './cascade-item';


/** Display a cascade of manifests */
export default function ManifestCascade({ columns: columnCount, manifestGroups })
{
    const columnClass = `col-xs-${(12 / columnCount) | 0}`;
    let columnContents;

    if (columnCount === 1)
        columnContents = [manifestGroups.flatten(true).toArray()];
    else
        columnContents = computeColumns(columnCount, manifestGroups);

    return (
        <div className="row">
            {columnContents.map((manifests, i) => (
                <div key={i} className={columnClass}>
                    {manifests.map((m, j) => <ManifestCascadeItem key={j} manifest={m} />)}
                </div>
            ))}
        </div>
    );
}

ManifestCascade.propTypes = {
    columns: PropTypes.number.isRequired,
    manifestGroups: PropTypes.instanceOf(Im.List).isRequired
};

/**
 * Compute columns of approcimately equal height with the property
 * that manifests never occur in the same columns below manifests
 * in a later group.
 *
 * @param columnCount
 * @param manifestGroups
 * @returns {Array<Array>} Columns
 */
function computeColumns(columnCount, manifestGroups)
{
    const columnHeights = Im.Repeat(0, columnCount).toArray();
    const columnContents = Im.Repeat(Im.List(), columnCount).toJS();

    for (const group of manifestGroups)
    {
        const layout = getGroupLayout(group, columnHeights);

        // Push the manifests to their columns
        for (const [index, newManifests] of layout.entries())
        {
            for (const manifest of newManifests)
            {
                columnHeights[index] += getHeight(manifest);
                columnContents[index].push(manifest);
            }
        }
    }

    return columnContents;
}

/**
 * Find the assignment which minimizes the difference between shortest and
 * greatest column height.
 */
function getGroupLayout(group, columnHeights)
{
    // Derive all the assignments of manifests to columns which have different heights
    const layouts = group.reduce((layouts, manifest) => (
        layouts.flatMap(cols => appendedToEachColumn(cols, manifest))
    ), Im.List.of(Im.Repeat(Im.List(), columnHeights.length).toList()));

    return layouts.map(layout =>
    {
        const addHeights = (totalHeight, manifest) =>
        {
            return totalHeight + getHeight(manifest);
        };

        const newHeights = layout.map((col, i) =>
        {
            return col.reduce(addHeights, columnHeights[i]);
        });

        return {
            layout,
            difference: Math.max(...newHeights) - Math.min(...newHeights)
        };
    }).reduce((best, current) => current.difference < best.difference ? current : best).layout;
}

/**
 * Return a sequence of column lists such that in the nth list in the sequence
 * the manifest is appended to the nth column.
 */
function appendedToEachColumn(cols, manifest)
{
    return Im.Range(0, cols.size)
        .map(i => cols.update(i, col => col.push(manifest)));
}

/**
 * Get the height of the manifest card.
 *
 * TODO(wabain): For now this returns a constant placeholder
 *
 * @param manifest
 * @returns {Number}
 */
function getHeight(manifest) // eslint-disable-line no-unused-vars
{
    return PLACEHOLDER_MANIFEST_HEIGHT;
}

export const __hotReload = true;
