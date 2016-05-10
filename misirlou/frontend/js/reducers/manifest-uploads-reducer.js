import Im from 'immutable';

import { MANIFEST_UPLOAD } from '../actions';
import ManifestUploadStatusResource from '../resources/manifest-upload-status-resource';

const initialState = Im.Map();

/**
 * Update state on manifest upload status changes (*not* manifest request
 * status changes.
 */
export default function reduceManifestUploads(state = initialState, action = {})
{
    switch (action.type)
    {
        case MANIFEST_UPLOAD:
            return registerUpdate(state, action.payload);

        default:
            return state;
    }
}

/** Update the status of the manifest upload for the manifest at remoteUrl */
function registerUpdate(state, { status, remoteUrl, error, url })
{
    return state.update(remoteUrl, (upload = new ManifestUploadStatusResource({ remoteUrl })) =>
    {
        return upload.setStatus(status, error || (url ? { url } : null));
    });
}

