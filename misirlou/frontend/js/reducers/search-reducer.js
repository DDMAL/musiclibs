import Im from 'immutable';
import { SEARCH_REQUEST_STATUS_CHANGE } from '../actions';
import AsyncStatusRecord, { AsyncErrorRecord, ERROR, SUCCESS } from '../async-status-record';

const initialState = Im.Map();

const SearchRecord = Im.Record({
    numFound: 0,
    nextPage: null,
    results: Im.List()
});

const SearchResultRecord = Im.Record({
    id: null,
    label: null,
    description: null,
    thumbnail: null,
    attribution: null
});

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
    const existing = state.get(query);

    let value = existing ? existing.value : null;

    if (status === ERROR)
    {
        value = AsyncErrorRecord({ error });
    }
    else if (status === SUCCESS)
    {
        value = (value || SearchRecord()).merge({
            numFound: response['num_found'],
            nextPage: response.next
        }).update('results', old => old.concat(Im.Seq(response.results).map(getResultRecord)));
    }

    return state.set(query, AsyncStatusRecord({
        status,
        value
    }));
}

/** Convert a search result object from the web API into a local, normalized result */
function getResultRecord(result)
{
    return SearchResultRecord({
        id: result['local_id'],
        label: result.label,
        description: result.description,
        thumbnail: result.thumbnail,
        attribution: result.attribution
    });
}

export const __hotReload = true;
