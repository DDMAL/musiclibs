import Im from 'immutable';
import { SEARCH_REQUEST_STATUS_CHANGE } from '../actions';
import AsyncStatusRecord, { AsyncErrorRecord, ERROR, SUCCESS } from '../async-status-record';

const initialState = Im.Map();

/**
 * Update the state when a request for a search is made or completed
 */
export default function reduceSearches(state = initialState, action = {})
{
    switch (action.type)
    {
        case SEARCH_REQUEST_STATUS_CHANGE:
            return updateSearches(state, action.payload);

        default:
            return state;
    }
}

/**
 * Update the state by setting the value of the query to reflect the
 * new status.
 *
 * @param state
 * @param payload
 * @returns Im.Map<String,AsyncStatusRecord>
 */
export function updateSearches(state, { status, query, response, error })
{
    let value = null;

    if (status === ERROR)
    {
        value = AsyncErrorRecord({ error });
    }
    else if (status === SUCCESS)
    {
        value = Im.List(response ? response.results : null);
    }

    return state.set(query, AsyncStatusRecord({
        status,
        value
    }));
}

export const __hotReload = true;
