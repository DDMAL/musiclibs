import * as OMR from '../api/omr';

export function requestHighlightLocations(manifestId, pageIndex, pitchQuery)
{
    return (dispatch, getState) =>
    {
        const state = getState();
        if (state.manifests[manifestId] && state.manifests[manifestId].omrSearchResults[pageIndex])
            return;

        return OMR.getLocations(manifestId, pageIndex, pitchQuery);
    }
}

