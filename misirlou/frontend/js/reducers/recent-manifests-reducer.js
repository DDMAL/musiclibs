import Im from 'immutable';
import { RECENT_MANIFESTS_REQUEST } from '../actions';

import RecentManifestsResource from '../resources/recent-manifests-resource';

/**
 * Update the state when a request for a manifest is made or completed,
 * or when a manifest is successfully uploaded.
 */
export default function reduceRecentManifests(state = new RecentManifestsResource(), action = {})
{
    switch (action.type)
    {
        case RECENT_MANIFESTS_REQUEST:
            return handleStatusChange(state, action.payload);

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
 * @returns RecentManifestsResource
 */
export function handleStatusChange(state, { status, resource, error })
{
    let value;

    if (resource)
    {
        value = {
            list: Im.Seq(resource).map(info => info.id).toList()
        };
    }
    else if (error)
    {
        value = error;
    }

    return state.setStatus(status, value);
}

