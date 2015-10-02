import Im from 'immutable';

import { MANIFEST_UPLOAD_STATUS_CHANGE } from '../actions.js';
import { ERROR } from '../action-creators/manifest-upload';

const ManifestRecord = Im.Record({ status: null, error: null });

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
function registerUpdate(state, { status, remoteUrl, error })
{
    return state.update(remoteUrl, defaultRecord, record =>
    {
        return record.merge({
            status,
            error: status === ERROR ? error : null
        });
    });
}

export const __hotReload = true;
