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
    }).then((response) =>
    {
        // Turn a 400 response into a failed import of the source URL
        if (response.status === 400)
        {
            return response.json().then((body) => ({
                total: 1,
                succeeded: [],
                failed: [
                    {
                        sourceUrl: remoteUrl,
                        localUrl: null,
                        warnings: [],
                        errors: body.errors
                    }
                ]
            }));
        }

        // Otherwise, treat the initial request as successful and poll for the eventual resolution
        return Promise.resolve(response)
            .then(expectStatus(202))
            .then(getJson)
            .then(json =>
            {
                return pollUploadStatus(json.status);
            });
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
                    return {
                        total: body['total_count'],
                        succeeded: getImportRecord(body.succeeded),
                        failed: getImportRecord(body.failed)
                    };

                default:
                    // For now just keep going if given an unrecognized status
                    return continuePolling();
            }
        });
    });
}

function getImportRecord(importResultObject)
{
    return Object.entries(importResultObject).map(([key, value]) =>
    {
        return {
            sourceUrl: key,
            localUrl: value.url || null,
            warnings: value.warnings || [],
            errors: value.errors || []
        };
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

