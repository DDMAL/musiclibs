import Im from 'immutable';
import { SEARCH_REQUEST_STATUS_CHANGE } from '../actions';
import Resource from '../resource-record';

const SearchRecord = Im.Record({
    query: null,
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
export default function reduceSearches(state = null, action = {})
{
    switch (action.type)
    {
        case SEARCH_REQUEST_STATUS_CHANGE:
            return updateSearch(state, action.payload);

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
export function updateSearch(state, { status, query, newSearch, response, error })
{
    if (newSearch || state === null || state.value.query !== query)
    {
        state = new Resource({
            value: SearchRecord({
                query
            })
        });
    }

    return state.setStatus(status, error || response, addSearchResults);
}

/**
 * Update a search record with the values given in the new response
 *
 * @param {SearchRecord} search
 * @param newResponse
 * @returns {SearchRecord}
 */
export function addSearchResults(search, newResponse)
{
    return search.merge({
        numFound: newResponse['num_found'],
        nextPage: newResponse.next
    })
    .update('results', results =>
    {
        const newRecords = Im.Seq(newResponse.results).map(getResultRecord);
        return results.concat(newRecords);
    });
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
