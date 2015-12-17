import { MANIFEST_REQUEST_STATUS_CHANGE } from '../actions';
import * as Manifests from '../api/manifests';
import { ERROR, PENDING, SUCCESS } from '../async-request-status';

/**
 * Request the manifest with the given ID if it is not cached, or if
 * the cached request yielded an error.
 */
export function request({ id })
{
    return (dispatch, getState) =>
    {
        const cached = getState().manifests.get(id);

        if (cached && cached.status !== ERROR)
            return;

        dispatch(getRequestStatusAction(PENDING, id));

        Manifests.get(id)
            .then(resource =>
            {
                dispatch(getRequestStatusAction(SUCCESS, id, { resource }));
            },
            error =>
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
