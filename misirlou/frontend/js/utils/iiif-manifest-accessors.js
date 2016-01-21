/**
 * @module
 *
 * Basic utilities for working with IIIF Presentation API manifests
 */

import Im from 'immutable';

import { getLinks, getValues } from './json-ld-accessors';

/**
 * Get a URL from a IIIF image API descriptor,
 * using the specified width.
 *
 * @param {Object} image
 * @param {number} maxWidth
 * @returns {?{ url: string, height: number, width: number }}
 */
export function getImageUrlWithMaxWidth(image, maxWidth)
{
    if (!isImageType(image) || !image.service)
        return null;

    const width = Math.min(maxWidth, image.width);
    const height = image.height * (width / image.width);

    if (isNaN(height))
        return null;

    const url = getImageUrl(image.service, width);

    if (url === null)
        return null;

    return { url, width, height };
}

/**
 * @param image
 * @returns {Boolean}
 */
function isImageType(image)
{
    if (!image)
        return false;

    const type = image['@type'];

    return isImageTypeString(type) || Array.isArray(type) && type.some(isImageTypeString);
}

/**
 * Wellcome has the type camelCased, so we just normalize the case first
 * (even though I'm pretty sure JSON-LD types are case-sensitive)
 */
function isImageTypeString(type)
{
    return typeof type === 'string' && type.toLowerCase() === 'dctypes:image';
}

/**
 * Get the IIIF Image API URL for the image with the specified width
 * and the aspect ratio preserved.
 *
 * @param svc
 * @param width
 * @returns {?string}
 */
function getImageUrl(svc, width)
{
    const context = svc['@context'];

    let quality;

    switch (context)
    {
        case 'http://iiif.io/api/image/1/context.json':
            quality = 'native';
            break;

        case 'http://iiif.io/api/image/2/context.json':
            quality = 'default';
            break;

        default:
            return null;
    }

    return `${svc['@id']}/full/${width},/0/${quality}.jpg`;
}

/**
 * Return a list of { label, hrefs } pairs with links to external
 * resources specified in a manifest
 *
 * @param manifest
 * @returns {{ text: string, links: string[] }[]}
 */
export function getManifestLinks(manifest)
{
    // TODO: Use specified labels if available

    return Im.Seq({
        related: 'Related material',
        within: 'Collection',
        seeAlso: 'Additional data'
    })
    .map((label, key) => ({ label, hrefs: getLinks(manifest[key]) }))
    .filter(link => link.hrefs.length > 0)
    .toArray();
}

/**
 * Map key/value metadata pairs into validated { term, description } objects with
 * string values.
 *
 * @returns {{ term: string, description: string }[]}
 */
export function getMetadataTerms(metadata, preferredLanguage)
{
    if (!Array.isArray(metadata))
        return [];

    return metadata.map(pairing =>
    {
        if (!pairing)
            return null;

        let { label, value } = pairing;

        label = getValues(label, preferredLanguage);
        value = getValues(value, preferredLanguage);

        if (label.length === 0 || value.length === 0)
            return null;

        // FIXME(wabain): Handle multiple values better (how would that occur?)
        return {
            term: label.join('; '),
            description: value.join('; ')
        };
    }).filter(term => term !== null);
}
