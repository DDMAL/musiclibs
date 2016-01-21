import React, { PropTypes } from 'react';
import Im from 'immutable';

import { getImageUrlWithMaxWidth } from '../../../utils/iiif-manifest-accessors';
import { getLinks } from '../../../utils/json-ld-accessors';

import ManifestCascadeItem from './cascade-item';


const THUMBNAIL_MAX_WIDTH = 500;
const THUMBNAIL_FALLBACK_HEIGHT = 250;


/** Display a cascade of manifests */
export default function ManifestCascade({ columns: columnCount, manifestGroups })
{
    const columnClass = `col-xs-${(12 / columnCount) | 0}`;

    const manifestInfo = manifestGroups.map(manifests => manifests.map(manifest =>
    {
        let height = THUMBNAIL_FALLBACK_HEIGHT;
        let url = null;

        if (manifest.remoteManifestLoaded)
        {
            const thumbnail = getThumbnail(manifest.value.manifest);

            if (thumbnail)
            {
                height = thumbnail.height;
                url = thumbnail.url;
            }
        }

        return {
            manifest,
            height,
            img: url
        };
    }));

    let columnContents;

    if (columnCount === 1)
        columnContents = [manifestInfo.flatten(true).toArray()];
    else
        columnContents = computeColumns(columnCount, manifestInfo);

    return (
        <div className="row">
            {columnContents.map((manifests, i) => (
                <div key={i} className={columnClass}>
                    {manifests.map((info, j) => (
                        <ManifestCascadeItem key={j} {...info} />
                    ))}
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
 * @param manifestInfoGroups
 * @returns {Array<Array>} Columns
 */
function computeColumns(columnCount, manifestInfoGroups)
{
    const columnHeights = Im.Repeat(0, columnCount).toArray();
    const columnContents = Im.Repeat(Im.List(), columnCount).toJS();

    for (const infoGroup of manifestInfoGroups)
    {
        const layout = getGroupLayout(infoGroup, columnHeights);

        // Push the manifests to their columns
        for (const [index, newManifests] of layout.entries())
        {
            for (const info of newManifests)
            {
                columnHeights[index] += info.height;
                columnContents[index].push(info);
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

    const addHeights = (totalHeight, info) =>
    {
        return totalHeight + info.height;
    };

    return layouts.map(layout =>
    {
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
 * @param manifest IIIF Presentation API manifest
 * @returns ?{{ url: string, width: number, height: number }}
 */
function getThumbnail(manifest)
{
    if (manifest.thumbnail)
    {
        const thumbnail = getThumbnailFromField(manifest.thumbnail);

        if (thumbnail)
            return thumbnail;
    }

    const sequence = getArrayEntry(manifest, 'sequences');

    if (!sequence)
        return null;

    const canvas = getArrayEntry(sequence, 'canvases', arr => arr[Math.floor(arr.length / 2)]);

    if (!canvas)
        return null;

    const image = getArrayEntry(canvas, 'images');

    if (!image || !image.resource || !image.resource.service)
        return null;

    const urlSpec = getImageUrlWithMaxWidth(image.resource, THUMBNAIL_MAX_WIDTH);

    if (urlSpec)
        return urlSpec;

    if (canvas.thumbnail)
        return getThumbnailFromField(canvas.thumbnail);

    return null;
}

/**
 * @param thumbnail
 * @returns ?{{ url: string, width: number, height: number }}
 */
function getThumbnailFromField(thumbnail)
{
    // If the thumbnail is a plain URL, just treat it as being a square of the maximum
    // allowed size
    if (typeof thumbnail === 'string')
        return { url: thumbnail, width: THUMBNAIL_MAX_WIDTH, height: THUMBNAIL_MAX_WIDTH };

    if (typeof thumbnail !== 'object' || thumbnail === null)
        return null;

    if (Array.isArray(thumbnail))
        return getThumbnailFromField(thumbnail[0]);

    if (thumbnail.service)
    {
        const tailored = getImageUrlWithMaxWidth(thumbnail, THUMBNAIL_MAX_WIDTH);

        if (tailored)
            return tailored;
    }

    const ids = getLinks(thumbnail);

    if (ids.length < 1)
        return null;

    return {
        url: ids[0],
        width: thumbnail.width,
        height: thumbnail.height
    };
}

/**
 * @param {Object<String, Array<T>>} obj
 * @param {string} key
 * @param {function(string): T} getter
 * @returns {?T}
 */
function getArrayEntry(obj, key, getter = getFirst)
{
    const list = obj[key];

    if (!Array.isArray(list) || list.length === 0)
        return null;

    return getter(list);
}

/**
 * Get the first entry in an array
 *
 * @param {Array<T>} arr
 * @returns {T}
 */
function getFirst(arr)
{
    return arr[0];
}

export const __hotReload = true;
