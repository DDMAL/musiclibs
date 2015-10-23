import Im from 'immutable';

import { MANIFEST_UPLOAD_STATUS_CHANGE } from '../actions.js';
import { ERROR, SUCCESS } from '../action-creators/manifest-upload';

const ManifestRecord = Im.Record({ status: null, error: null, url: null });

const initialState = Im.Map();
const defaultRecord = ManifestRecord();

export default function reduceManifestUploads(state = initialState, action = {})
{
    switch (action.type)
    {
        case MANIFEST_UPLOAD_STATUS_CHANGE:
            return registerUpdate(state, action.payload);

        default:
            return state;
    }
}

/** Update the status of the manifest upload for the manifest at remoteUrl */
function registerUpdate(state, { status, remoteUrl, error, url })
{
    return state.update(remoteUrl, defaultRecord, record =>
    {
        return record.merge({
            status,
            error: status === ERROR ? error : null,
            url: status === SUCCESS ? url : null
        });
    });
}

export const __hotReload = true;
