import Im from 'immutable';
import { MANIFEST_REQUEST_STATUS_CHANGE, MANIFEST_UPLOAD_STATUS_CHANGE } from '../actions';
import AsyncStatusRecord, { AsyncErrorRecord, ERROR, SUCCESS } from '../async-status-record';

const ManifestRecord = Im.Record({ uuid: null, remoteUrl: null });

const initialState = Im.Map();

/**
 * Update the state when a request for a manifest is made or completed,
 * or when a manifest is successfully uploaded.
 */
export default function reduceManifests(state = initialState, action = {})
{
    switch (action.type)
    {
        case MANIFEST_REQUEST_STATUS_CHANGE:
            return registerManifest(state, action.payload.uuid, action.payload);

        case MANIFEST_UPLOAD_STATUS_CHANGE:
            // Only handle upload actions if the upload was successful
            if (action.payload.status === SUCCESS)
                return registerManifest(state, action.payload.resource.uuid, action.payload);

            return state;

        default:
            return state;
    }
}

/**
 * Update the state by setting the value of the manuscript to reflect the
 * new status.
 *
 * @param state
 * @param uuid
 * @param payload
 * @returns Im.Map<String,AsyncStatusRecord>
 */
export function registerManifest(state, uuid, { status, resource, error })
{
    let value = null;

    if (status === ERROR)
    {
        value = AsyncErrorRecord({ error });
    }
    else if (status === SUCCESS)
    {
        value = ManifestRecord({
            uuid,
            remoteUrl: resource['remote_url']
        });
    }

    return state.set(uuid, AsyncStatusRecord({
        status,
        value
    }));
}

export const __hotReload = true;
