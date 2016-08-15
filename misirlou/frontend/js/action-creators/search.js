import debounce from 'lodash.debounce';

import { PENDING, ERROR, SUCCESS } from '../async-request-status';
import { SEARCH_REQUEST, SUGGEST_SEARCH_QUERIES, CLEAR_SEARCH, GET_STATS } from '../actions';

import * as Search from '../api/search';


const DEBOUNCE_INTERVAL = 500;


/**
 * Load the first page of search results, ensuring that requests are throttled.
 * Cached results are cleared.
 */
export function request({ query, pitchQuery, suggestions = false })
{
    return (dispatch) =>
    {
        dispatch(getSearchAction(PENDING, query, pitchQuery));
        execSearch(query, pitchQuery, dispatch, suggestions);
    };
}

/**
 * Load the next page of search results for the given query. This is a no-op if the
 * query isn't the current one or if the search resource isn't in a success state.
 */
export function loadNextPage({ query, pitchQuery })
{
    return (dispatch, getState) =>
    {
        const existing = getState().search.current;

        if (existing.query !== query || existing.pitchQuery !== pitchQuery || !existing.value.nextPage)
            return;

        dispatch(getSearchAction(PENDING, query, pitchQuery));

        Search.loadPage(existing.value.nextPage).then(
            response => dispatch(getSearchAction(SUCCESS, query, pitchQuery, { response })),
            error => dispatch(getSearchAction(ERROR, query, pitchQuery, { error }))
        );
    };
}

/** Clear the search results */
export function clear()
{
    return {
        type: CLEAR_SEARCH
    };
}

/** Get stats to display under search bar. **/
export function getStats()
{
    return (dispatch, getState) =>
    {
        const existing = getState().stats;

        if (existing !== null)
        {
            return;
        }
        Search.getStats().then(
            response => dispatch({ type: GET_STATS, response })
        );
    };
}

const execSearch = debounce((query, pitchQuery, dispatch, getSuggestions) =>
{
    if (!query && !pitchQuery)
    {
        dispatch(clear());
        return;
    }

    dispatch(searchAction(query, pitchQuery));

    if (getSuggestions)
    {
        // TODO: Should this do something on errors?
        Search.getSuggestions(query).then(suggestions =>
        {
            dispatch({
                type: SUGGEST_SEARCH_QUERIES,
                payload: {
                    query,
                    suggestions
                }
            });
        });
    }
}, DEBOUNCE_INTERVAL);

const searchAction = (query, pitchQuery) =>
{
    return (dispatch, getState) =>
    {
        // By checking that the query is in the same state as it was when the request was made,
        // we ensure that a delayed request doesn't replace the most recent results
        const startState = getState().search.current;

        Search.get(query, pitchQuery).then(
            response => getSearchAction(SUCCESS, query, pitchQuery, { response }),
            error => getSearchAction(ERROR, query, pitchQuery, { error })
        ).then(
            response =>
            {
                if (startState.query === getState().search.current.query &&
                    startState.pitchQuery === getState().search.current.pitchQuery)
                    dispatch(response);
            }
        );
    };
};

/** Get a search status change action for the given status and query */
function getSearchAction(status, query, pitchQuery, extra = null)
{
    return {
        type: SEARCH_REQUEST,
        payload: {
            ...extra,
            status,
            query,
            pitchQuery
        }
    };
}


