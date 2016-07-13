import { MANIFEST_REQUEST, RECENT_MANIFESTS_REQUEST,
    MANIFEST_OMR_LOCATION_REQUEST, MANIFEST_OMR_LOCATION_CLEAR } from '../actions';
import { ERROR, PENDING, SUCCESS } from '../async-request-status';

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

        if (cached && (cached.status === PENDING || cached.status === SUCCESS))
            return null;

        dispatch(getRequestStatusAction(PENDING, id));

        return Manifests.get(id).then(manifest =>
        {
            dispatch(getRequestStatusAction(SUCCESS, id, { manifest }));
        }, error =>
        {
            dispatch(getRequestStatusAction(ERROR, id, { error }));
        });
    };
}

export function requestRecent()
{
    return (dispatch, getState) =>
    {
        const cached = getState().recentManifests;

        if (cached && cached.status === PENDING)
            return;

        dispatch(getRecentRequestStatusAction(PENDING));

        return Manifests.getRecent()
            .then(response =>
            {
                dispatch(getRecentRequestStatusAction(SUCCESS, {
                    resource: response.results
                }));
            },
            error =>
            {
                dispatch(getRecentRequestStatusAction(ERROR, { error }));
            });
    };
}

export function requestHighlightLocations(manifestId, pageIndex, pitchQuery)
{
    return (dispatch, getState) =>
    {
        if (!pitchQuery)
            return;

        const state = getState();
        if (state.manifests[manifestId] && state.manifests[manifestId].omrSearchResults[pageIndex])
            return;

        dispatch(getRequestHighlightStatusAction(PENDING, manifestId, pageIndex));

        return Manifests.getLocations(manifestId, pageIndex, pitchQuery)
            .then(response =>
            {
                dispatch(getRequestHighlightStatusAction(SUCCESS, manifestId, pageIndex, { omrSearchResults: response }));
            },
            error =>
            {
                dispatch(getRequestHighlightStatusAction(ERROR, manifestId, pageIndex, { error }));
            });
    }
}

export function clearHighlightLocations(manifestId)
{
    return (dispatch, getState) =>
    {
        dispatch({
            type: MANIFEST_OMR_LOCATION_CLEAR,
            payload: {
                manifestId
            }
        });
    }
}

/** Create a status change action for recent manifests */
function getRecentRequestStatusAction(status, extra = null)
{
    return {
        type: RECENT_MANIFESTS_REQUEST,
        payload: {
            ...extra,
            status
        }
    };
}

/** Create a status change action for the manifest with the ID */
function getRequestStatusAction(status, id, extra = null)
{
    return {
        type: MANIFEST_REQUEST,
        payload: {
            ...extra,
            status,
            id
        }
    };
}

/** Create a status change action for recent manifests */
function getRequestHighlightStatusAction(status, manifestId, pageIndex, extra = null)
{
    return {
        type: MANIFEST_OMR_LOCATION_REQUEST,
        payload: {
            ...extra,
            manifestId,
            pageIndex,
            status
        }
    };
}
