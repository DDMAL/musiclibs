import Im from 'immutable';

import { MANIFEST_UPLOAD_STATUS_CHANGE } from '../actions';
import AsyncStatusRecord, { AsyncErrorRecord, ERROR, SUCCESS } from '../async-status-record';

const UploadSuccessRecord = Im.Record({ url: null });

const initialState = Im.Map();

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
    let value = null;

    if (status === ERROR)
        value = AsyncErrorRecord({ error });
    else if (status === SUCCESS)
        value = UploadSuccessRecord({ url });

    return state.set(remoteUrl, AsyncStatusRecord({ status, value }));
}

export const __hotReload = true;
