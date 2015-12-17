import Im from 'immutable';
import { MANIFEST_REQUEST_STATUS_CHANGE, MANIFEST_UPLOAD_STATUS_CHANGE } from '../actions';
import { SUCCESS } from '../async-status-record';
import ManifestResource from '../resources/manifest-resource';

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
            return registerManifest(state, action.payload.id, action.payload);

        case MANIFEST_UPLOAD_STATUS_CHANGE:
            // Only handle upload actions if the upload was successful
            if (action.payload.status === SUCCESS)
                return registerManifest(state, action.payload.resource.id, action.payload);

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
 * @param id
 * @param payload
 * @returns Im.Map<String,ManifestResource>
 */
export function registerManifest(state, id, { status, resource, error })
{
    return state.update(id, (res = new ManifestResource({ id })) =>
    {
        return res.setStatus(status, error || resource && { remoteUrl: resource['remote_url'] });
    });
}

export const __hotReload = true;
