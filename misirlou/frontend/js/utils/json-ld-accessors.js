/**
 * @module
 * Basic utilities for working with JSON-LD [1] documents.
 *
 * Note that these functions don't take into account the JSON-LD
 * context automatically; it's up to the user to call getLinks
 * for terms which represent links and getValues for terms which
 * represent values.
 *
 * [1]: http://json-ld.org/
 */

const INVALID_LANGUAGE = Symbol('invalid language');


/**
 * @param {Array<string|Object>|string|Object} value
 * @returns {Array<string>}
 */
export function getLinks(value)
{
    if (!value)
        return [];

    if (typeof value === 'string')
        return [value];

    return getLinks(value['@id']);
}


/**
 * Return, in order of declining preference:
 *
 *  1. all the values of the property which have the preferred language,
 *     or if there are no such properties then
 *  2. all properties which do not have the language declared, or if there
 *     are no such properties then
 *  3. the first property, regardless of its language, or
 *  4. an empty array
 *
 * @param property
 * @param preferredLanguage
 * @returns {Array<string>}
 */
export function getValues(property, preferredLanguage)
{
    let normalized = normalizeProperty(property);

    // Short path: No choices to make
    if (normalized.length <= 1)
        return normalized.map(entry => entry.value);
    if (typeof normalized[Symbol.iterator] !== 'function')
        normalized = [normalized];

    const preferred = [];
    const unspecified = [];
    const wrongLanguage = [];

    for (const entry of normalized)
    {
        if (!entry.lang)
            unspecified.push(entry.value);
        else if (langMatches(entry.lang, preferredLanguage))
            preferred.push(entry.value);
        else
            wrongLanguage.push(entry.value);
    }

    if (preferred.length > 0)
        return preferred;

    if (unspecified.length > 0)
        return unspecified;

    return wrongLanguage.slice(0, 1);
}


function normalizeProperty(prop)
{
    if (!prop)
        return [];

    if (typeof prop === 'string')
        return [{ value: prop, lang: null }];

    if (Array.isArray(prop))
        return prop.map(normalizeProperty).filter(p => p !== null);

    if (typeof prop === 'object')
    {
        const value = prop['@value'];

        if (!value || typeof value !== 'string')
            return [];

        let lang = prop['@language'];

        if (!lang)
            lang = null;

        if (typeof lang !== 'string')
            lang = INVALID_LANGUAGE;

        return { value, lang };
    }

    return [];
}

function langMatches(actual, preferred)
{
    if (!actual || actual === INVALID_LANGUAGE)
        return false;

    return actual === preferred || actual.slice(0, actual.indexOf('-')) === preferred;
}

