import { expectStatus, getJson } from './utils';

/**
 * Make an HTTP GET request for the query and return a promise
 * which resolves if the request succeeds
 */
export function get(query)
{
    const url = `/search?q=${encodeURIComponent(query)}`;
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
    .then(getJson);
}
