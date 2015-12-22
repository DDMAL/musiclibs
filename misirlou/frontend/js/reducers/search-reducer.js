import Im from 'immutable';
import { SEARCH_REQUEST_STATUS_CHANGE, CLEAR_SEARCH } from '../actions';
import SearchResource from '../resources/search-resource';
import { SUCCESS } from '../async-request-status';

const SearchStateRecord = Im.Record({
    current: new SearchResource(),
    stale: new SearchResource()
});

const SearchResultRecord = Im.Record({
    id: null,
    label: null,
    description: null,
    thumbnail: null,
    attribution: null,
    hits: null
});

/**
 * Update the state when a request for a search is made or completed
 */
export default function reduceSearches(state = SearchStateRecord(), action = {})
{
    switch (action.type)
    {
        case SEARCH_REQUEST_STATUS_CHANGE:
            // If the current search is out of date but did go through, copy it to the
            // stale search field
            if (action.payload.query !== state.current.query && state.current.status === SUCCESS)
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
 * @returns Im.Map<String,SearchResource>
 */
export function updateSearch(search, { status, query, response, error })
{
    if (search.query !== query)
    {
        search = new SearchResource({ query });
    }

    return search.setStatus(status, error || response, addSearchResults);
}

/**
 * Update a search record with the values given in the new response
 *
 * @param {SearchValue} search
 * @param newResponse
 * @returns {SearchValue}
 */
export function addSearchResults(search, newResponse)
{
    const newRecords = Im.Seq(newResponse.results).map(getResultRecord);

    return search
        .set('numFound', newResponse['num_found'])
        .set('nextPage', newResponse.next)
        .set('spellcheck', newResponse.spellcheck)
        .update('results', results => results.concat(newRecords));
}

/** Convert a search result object from the web API into the local result type */
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
