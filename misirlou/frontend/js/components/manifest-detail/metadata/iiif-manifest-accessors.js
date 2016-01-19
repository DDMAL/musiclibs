/**
 * @module
 *
 * Basic utilities for working with IIIF Presentation API manifests
 */

import Im from 'immutable';

import { getLinks, getValues } from './json-ld-accessors';

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
