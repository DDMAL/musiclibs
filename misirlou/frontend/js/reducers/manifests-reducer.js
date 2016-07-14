import Im from 'immutable';

import { RECENT_MANIFESTS_REQUEST, MANIFEST_REQUEST, MANIFEST_UPLOAD,
    MANIFEST_OMR_LOCATION_REQUEST, MANIFEST_OMR_LOCATION_CLEAR } from '../actions';
import { SUCCESS } from '../async-request-status';

import ManifestResource from '../resources/manifest-resource';
import OMRSearchResultsResource from '../resources/omr-results-resource';

export const SUCCESS_LOCAL = 'success_local';

const initialState = Im.Map();

/**
 * Update the state when a request for a manifest is made or completed,
 * or when a manifest is successfully uploaded.
 */
export default function reduceManifests(state = initialState, action = {})
{
    switch (action.type)
    {
        case MANIFEST_REQUEST:
            return registerManifest(state, action.payload);

        case MANIFEST_UPLOAD:
            // Only handle upload actions if the upload was successful
            if (action.payload.status === SUCCESS)
                return registerUploadedManifest(state, action.payload.resource.id, action.payload.remoteUrl);

            return state;

        case RECENT_MANIFESTS_REQUEST:
            // We load recent manifests when the call succeeds
            if (action.payload.status === SUCCESS)
            {
                let newState = state;

                for (const manifest of action.payload.resource)
                {
                    newState = registerManifest(newState, {
                        status: SUCCESS_LOCAL,
                        id: manifest.id,
                        resource: manifest
                    });
                }

                return newState;
            }

            return state;

        case MANIFEST_OMR_LOCATION_REQUEST:
            return registerOmrResults(state, action.payload);

        case MANIFEST_OMR_LOCATION_CLEAR:
            return clearOmrResults(state, action.payload);

        default:
            return state;
    }
}

/**
 * Update the state by setting the value of the manuscript to reflect the
 * new status.
 *
 * @param state
 * @param payload
 * @returns Im.Map<String,ManifestResource>
 */
export function registerManifest(state, { id, status, manifest, error })
{
    return state.update(id, (res = new ManifestResource({ id })) =>
    {
        if (status === SUCCESS)
        {
            return res.set('remoteManifestLoaded', true)
                      .setStatus(status, { manifest });
        }

        return res.setStatus(status, error || null);
    });
}

/** Add an entry for a just-uploaded manifest */
export function registerUploadedManifest(state, id, remoteUrl)
{
    return state.set(id, (new ManifestResource({ id })).setStatus(SUCCESS, { remoteUrl }));
}

/** Add all OMR results to the current manifest, on the current page */
export function registerOmrResults(state, { status, omrSearchResults, manifestId, pageIndex, error })
{
    return state.updateIn([manifestId, 'value', 'omrSearchResults'], (omrSearchResultsValue) =>
    {
        if (!omrSearchResultsValue)
            omrSearchResultsValue = new OMRSearchResultsResource();

        if (status === SUCCESS)
        {
            return omrSearchResultsValue.setStatus(status, {
                highlights: Im.Map().set(pageIndex, omrSearchResults)
            });
        }

        return omrSearchResultsValue.setStatus(status, error || null);
    });
}

/** Remove all OMR results from the current manifest */
export function clearOmrResults(state, { manifestId })
{
    return state.setIn([manifestId, 'value', 'omrSearchResults'], null);
}
