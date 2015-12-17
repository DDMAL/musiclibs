import { MANIFEST_REQUEST_STATUS_CHANGE } from '../actions';
import { ERROR, PENDING, SUCCESS } from '../async-request-status';
import { SUCCESS_LOCAL } from '../reducers/manifests-reducer';

import * as Manifests from '../api/manifests';

/**
 * Request the manifest with the given ID if it is not cached, or if
 * the cached request yielded an error.
 */
export function request({ id })
{
    return (dispatch, getState) =>
    {
        const cached = getState().manifests.get(id);

        let remotePromise;

        if (cached)
        {
            if (cached.status === PENDING || cached.remoteManifestLoaded)
                return;

            // If we already have the local data then load the remote promise directly
            if (cached.value)
                remotePromise = Manifests.loadRemote(cached.value.remoteUrl);
        }

        dispatch(getRequestStatusAction(PENDING, id));

        // If we need the local data, get it and resolve with the remote promise
        if (!remotePromise)
        {
            remotePromise = Manifests.get(id).then(({ resource, remotePromise }) =>
            {
                dispatch(getRequestStatusAction(SUCCESS_LOCAL, id, { resource }));
                return remotePromise;
            });
        }

        // Handle the overall success/error cases
        remotePromise.then(manifest =>
        {
            dispatch(getRequestStatusAction(SUCCESS, id, { manifest }));
        }, error =>
        {
            dispatch(getRequestStatusAction(ERROR, id, { error }));
        });
    };
}

/** Create a status change action for the manifest with the ID */
function getRequestStatusAction(status, id, extra = null)
{
    return {
        type: MANIFEST_REQUEST_STATUS_CHANGE,
        payload: {
            ...extra,
            status,
            id
        }
    };
}

export const __hotReload = true;
