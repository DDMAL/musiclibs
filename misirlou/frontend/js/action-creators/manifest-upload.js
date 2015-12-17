import { MANIFEST_UPLOAD_STATUS_CHANGE } from '../actions';
import * as Manifests from '../api/manifests';
import { ERROR, PROCESSING, SUCCESS } from '../async-request-status';

// Re-export the constants for convenience
export { ERROR, PROCESSING, SUCCESS };

/** Action creator to upload a manifest, handling the underlying API calls */
export function upload({ remoteUrl })
{
    return dispatch =>
    {
        dispatch(getUploadStatusAction(PROCESSING, remoteUrl));

        Manifests.upload(remoteUrl)
        .then(({ url, resource }) =>
        {
            dispatch(getUploadStatusAction(SUCCESS, remoteUrl, { url, resource }));
        },
        error =>
        {
            dispatch(getUploadStatusAction(ERROR, remoteUrl, { error }));
        });
    };
}

/**
 * Action creator for client-side validation errors. These are
 * propagated in the same way as server errors. Takes an
 * object with `remoteUrl` and `message`
 */
export function validationFailed({ remoteUrl, message })
{
    return getUploadStatusAction(ERROR, remoteUrl, {
        error: new Manifests.ManifestUploadRejectionError(message)
    });
}

/** Create an appropriate action */
function getUploadStatusAction(status, remoteUrl, extra = null)
{
    return {
        type: MANIFEST_UPLOAD_STATUS_CHANGE,
        payload: {
            ...extra,
            status,
            remoteUrl
        }
    };
}

export const __hotReload = true;
