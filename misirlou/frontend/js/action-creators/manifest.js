import { MANIFEST_REQUEST_STATUS_CHANGE } from '../actions';
import * as Manifests from '../api/manifests';
import { ERROR, PROCESSING, SUCCESS } from '../async-status-record';

/**
 * Request the manifest with the given UUID if it is not cached, or if
 * the cached request yielded an error.
 */
export function request({ uuid })
{
    return (dispatch, getState) =>
    {
        const cached = getState().manifests.get(uuid);

        if (cached && cached.status !== ERROR)
            return;

        dispatch(getRequestStatusAction(PROCESSING, uuid));

        Manifests.get(uuid)
            .then(resource =>
            {
                dispatch(getRequestStatusAction(SUCCESS, uuid, { resource }));
            },
            error =>
            {
                dispatch(getRequestStatusAction(ERROR, uuid, { error }));
            });
    };
}

/** Create a status change action for the manifest with the UUID */
function getRequestStatusAction(status, uuid, extra = null)
{
    return {
        type: MANIFEST_REQUEST_STATUS_CHANGE,
        payload: {
            ...extra,
            status,
            uuid
        }
    };
}

export const __hotReload = true;
