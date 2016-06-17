import * as OMR from '../api/omr';
import { MANIFEST_OMR_LOCATION_REQUEST } from '../actions';

export function requestHighlightLocations(manifestId, pageIndex, pitchQuery)
{
    return (dispatch, getState) =>
    {
        const state = getState();
        if (state.manifests[manifestId] && state.manifests[manifestId].omrSearchResults[pageIndex])
            return;

        // TODO handle errors
        return OMR.getLocations(manifestId, pageIndex, pitchQuery).then(response =>
        {
            dispatch({
                type: MANIFEST_OMR_LOCATION_REQUEST,
                payload: {
                    omrSearchResults: response,
                    manifestId,
                    pageIndex
                }
            })
        });
    }
}

