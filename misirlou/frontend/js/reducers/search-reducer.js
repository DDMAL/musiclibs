import Im from 'immutable';

import { SEARCH_REQUEST, CLEAR_SEARCH, SUGGEST_SEARCH_QUERIES } from '../actions';
import SearchResource from '../resources/search-resource';
import { SUCCESS } from '../async-request-status';
import deepFreeze from '../utils/deep-freeze-object';

const SearchStateRecord = Im.Record({
    current: new SearchResource(),
    stale: new SearchResource()
});

/**
 * Update the state when a request for a search is made or completed
 */
export default function reduceSearches(state = SearchStateRecord(), action = {})
{
    switch (action.type)
    {
        case SEARCH_REQUEST:
            // If the current search is out of date but did go through, copy it to the
            // stale search field
            if (action.payload.query !== state.current.query
                && (!action.payload.pitchQuery || action.payload.pitchQuery !== state.current.pitchQuery)
                && state.current.status === SUCCESS)
                state = state.set('stale', state.current);

            return state.set('current', updateSearch(state.current, action.payload));

        case CLEAR_SEARCH:
            return SearchStateRecord();

        case SUGGEST_SEARCH_QUERIES:
            if (action.payload.query === state.current.query)
                return state.setIn(['current', 'suggestions'], Im.List(action.payload.suggestions));

            return state;

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
export function updateSearch(search, { status, query, pitchQuery, response, error })
{
    if (search.query !== query || search.pitchQuery !== pitchQuery)
    {
        search = new SearchResource({ query, pitchQuery });
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
    deepFreeze(newResponse.results);

    return search
        .set('numFound', newResponse['num_found'])
        .set('nextPage', newResponse.next)
        .set('spellcheck', newResponse.spellcheck)
        .update('results', results => results.concat(newResponse.results));
}
