import { expectStatus, getJson } from './utils';

export function getLocations(manifestId, pageIndex, pitchQuery)
{
    const url = `/manifests/${encodeURIComponent(manifestId)}/search/`
        + `?m=${encodeURIComponent(pitchQuery)}&p=${encodeURIComponent(pageIndex + 1)}`;
    return fetch(url, {
        method: 'get',
        headers: {
            Accept: 'application/json'
        }
    })
    .then(expectStatus(200))
    .then(getJson);
}
