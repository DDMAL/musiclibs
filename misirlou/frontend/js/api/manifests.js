import { expectStatus, getJson, RequestFailureError } from './utils';

const POLL_WAIT_MS = 1000;

const UPLOAD_ERROR = -1;
const UPLOAD_SUCCESS = 0;
const UPLOAD_PROCESSING = 1;

export class ManifestUploadRejectionError extends Error {
    constructor(message)
    {
        super();
        this.name = 'ManifestUploadRejectionError';
        this.message = message;
    }
}

/**
 * Make an HTTP GET request for data on the manifest with the ID and return
 * a promise which resolves with the local data on the manifest.
 */
export function get(id)
{
    return fetch(`/manifests/${encodeURIComponent(id)}/`, {
        method: 'get',
        headers: {
            Accept: 'application/json'
        }
    })
    .then(expectStatus(200))
    .then(getJson);
}

export function getRecent()
{
    return fetch('/manifests/recent/', {
        method: 'get',
        headers: {
            Accept: 'application/json'
        }
    })
    .then(expectStatus(200))
    .then(getJson);
}

/**
 * Make an HTTP GET request for the IIIF manifest at `remoteUrl`
 */
export function loadRemote(remoteUrl)
{
    return fetch(remoteUrl, {
        method: 'get',
        headers: {
            Accept: 'application/ld+json, application/json'
        }
    }).then(getJson);
}

/**
 * Upload the manifest at the remote URL and return a promise
 * which resolves with the body of the manifest.
 */
export function upload(remoteUrl)
{
    const body = JSON.stringify({
        remote_url: remoteUrl // eslint-disable-line camelcase
    });

    return fetch('/manifests/', {
        method: 'post',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body
    })
    .then(expectStatus(202))
    .then(getJson)
    .then(json =>
    {
        // Poll the upload status endpoint
        return pollUploadStatus(json.status);
    });
}

/**
 * Poll the status endpoint for the URL until the upload is reported to
 * be successful or returns an error. Return a promise which resolves or
 * throws accordingly.
 */
function pollUploadStatus(statusUrl)
{
    const continuePolling = () => wait(POLL_WAIT_MS).then(() => pollUploadStatus(statusUrl));

    return fetch(statusUrl, {
        headers: {
            Accept: 'application/json'
        }
    }).then(response =>
    {
        // Keep polling on error
        // FIXME(wabain): this should time out or something
        if (response.status >= 500)
            return continuePolling();

        if (response.status !== 200)
            throw new RequestFailureError(response);

        return response.json().then(body =>
        {
            switch (body.status)
            {
                case UPLOAD_PROCESSING:
                    return continuePolling();

                case UPLOAD_ERROR:
                    throw new ManifestUploadRejectionError(body.error);

                case UPLOAD_SUCCESS:
                    // The browser will probably just redirect, but let's run through anyway
                    return fetch(body.location, {
                        headers: {
                            Accept: 'application/json'
                        }
                    })
                    .then(expectStatus(200))
                    .then(getJson);

                default:
                    // For now just keep going if given an unrecognized status
                    // if the response doesn't look like an actual manifest
                    if (!body['remote_url'])
                        return continuePolling();

                    return {
                        url: response.url,
                        resource: body
                    };
            }
        });
    });
}

/** Return a promise which resolves after the given number of milliseconds */
function wait(ms)
{
    return new Promise(resolve =>
    {
        setTimeout(resolve, ms);
    });
}

