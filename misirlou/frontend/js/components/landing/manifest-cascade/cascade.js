import React, { PropTypes } from 'react';
import Im from 'immutable';

import ManifestCascadeItem from './cascade-item';

/** Display a cascade of manifests */
export default function ManifestCascade({ columns: columnCount, manifestGroups })
{
    const columnClass = `col-xs-${(12 / columnCount) | 0}`;
    let columnContents;

    if (columnCount === 1)
    {
        columnContents = [manifestGroups.flatten(true).toArray()];
    }
    else
    {
        const heights = Im.Repeat(0, columnCount).toArray();
        columnContents = Im.Repeat(Im.List(), columnCount).toJS();

        for (const group of manifestGroups)
        {
            // Derive all the assignments of manifests to columns which have different heights
            const layouts = group.reduce((layouts, manifest) => (
                layouts.flatMap(cols => appendedToEachColumn(cols, manifest))
            ), Im.List.of(Im.Repeat(Im.List(), columnCount).toList()));

            // Find the assignment which minimizes the difference between shortest and greatest column height
            const layout = layouts.map(layout =>
            {
                const newHeights = layout.map((col, i) => col.reduce((totalHeight, manifest) => totalHeight + manifest.height, heights[i]));

                return {
                    layout,
                    difference: Math.max(...newHeights) - Math.min(...newHeights)
                };
            }).reduce((best, current) => current.difference < best.difference ? current : best).layout;

            // Push the manifests to their columns
            layout.forEach((newManifests, index) =>
            {
                newManifests.forEach(manifest =>
                {
                    heights[index] += manifest.height;
                    columnContents[index].push(manifest);
                });
            });
        }
    }

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
 * Return a sequence of column lists such that in the nth list in the sequence
 * the manifest is appended to the nth column.
 */
function appendedToEachColumn(cols, manifest)
{
    return Im.Range(0, cols.size)
        .map(i => cols.update(i, col => col.push(manifest)));
}

export const __hotReload = true;
