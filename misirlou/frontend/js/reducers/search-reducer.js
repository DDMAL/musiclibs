import Im from 'immutable';
import { SEARCH_REQUEST_STATUS_CHANGE, CLEAR_SEARCH } from '../actions';
import Resource from '../resource-record';

const SearchRecord = Im.Record({
    query: null,
    numFound: null,
    nextPage: null,
    results: Im.List()
});

const SearchResultRecord = Im.Record({
    id: null,
    label: null,
    description: null,
    thumbnail: null,
    attribution: null,
    hits: null
});

const SearchStateRecord = Im.Record({
    current: new Resource({ value: SearchRecord() }),
    stale: new Resource({ value: SearchRecord() })
});

/**
 * Update the state when a request for a search is made or completed
 */
export default function reduceSearches(state = SearchStateRecord(), action = {})
{
    switch (action.type)
    {
        case SEARCH_REQUEST_STATUS_CHANGE:
            if (action.payload.query !== state.current.value.query)
                state = state.set('stale', state.current);

            return state.set('current', updateSearch(state.current, action.payload));

        case CLEAR_SEARCH:
            return SearchStateRecord();

        default:
            return state;
    }
}

/**
 * Update the state by setting the value of the query to reflect the
 * new status.
 *
 * @param search
 * @param payload
 * @returns Im.Map<String,AsyncStatusRecord>
 */
export function updateSearch(search, { status, query, response, error })
{
    if (search.value.query !== query)
    {
        search = new Resource({
            value: SearchRecord({
                query
            })
        });
    }

    return search.setStatus(status, error || response, addSearchResults);
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
        attribution: result.attribution,
        hits: Im.List(result.hits)
    });
}

export const __hotReload = true;
