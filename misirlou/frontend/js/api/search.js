import { expectStatus, getJson } from './utils';

/**
 * Make an HTTP GET request for the query and return a promise
 * which resolves if the request succeeds
 */
export function get(query)
{
    const url = `/?q=${encodeURIComponent(query)}`;
    return loadPage(url);
}

/**
 * Execute the request for a given result page,
 * returning a Promise.
 */
export function loadPage(url)
{
    return fetch(url, {
        method: 'get',
        headers: {
            Accept: 'application/json'
        }
    })
    .then(expectStatus(200))
    .then(getJson)
    .then(obj => obj.search);
}

/**
 * Query the suggester for ways to complete the query.
 */
export function getSuggestions(query)
{
    const url = `/suggest/?q=${encodeURIComponent(query)}`;
    return fetch(url, {
        method: 'get'
    })
    .then(expectStatus(200))
    .then(getJson)
    .then(obj => obj.suggestions);
}

/* Get stats to display under search bar. */
export function getStats() {
    return fetch('/stats/', {
        method: 'get'
    })
    .then(expectStatus(200))
    .then(getJson)
}