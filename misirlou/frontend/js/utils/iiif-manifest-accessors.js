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
 * @returns {?string}
 */
export function getImageUrlWithMaxWidth(image, maxWidth)
{
    if (!image.service)
        return null;

    let width;

    if (typeof image.width !== 'number' || Number.isNaN(image.width))
        width = maxWidth;
    else
        width = Math.min(maxWidth, image.width);

    return getImageUrl(image.service, width);
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

    if (typeof svc.profile === 'string' && svc.profile.indexOf('#level0') !== -1)
        return null;

    switch (context)
    {
        case 'http://library.stanford.edu/iiif/image-api/1.1/context.json':
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
    const get = (key) => getLinks(manifest[key]);

    return Im.Seq({
        'Related material': get('related'),
        'Collection': get('within'),
        // Handle see_also as a special case for e-codices
        'Additional data': get('seeAlso').concat(get('see_also'))
    })
        .filter((hrefs) => hrefs.length > 0)
        .map((hrefs, label) => ({ hrefs, label }))
        .toArray();
}

/**
 * Map key/value metadata pairs into validated { label, value } objects with
 * string values.
 *
 * @returns {{ label: string, value: string }[]}
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
            label: label.join('; '),
            value: value.join('; ')
        };
    }).filter(term => term !== null);
}
