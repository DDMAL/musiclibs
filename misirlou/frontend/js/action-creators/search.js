import debounce from 'lodash.debounce';

import { PENDING, ERROR, SUCCESS } from '../async-request-status';
import { SEARCH_REQUEST, SUGGEST_SEARCH_QUERIES, CLEAR_SEARCH, GET_STATS } from '../actions';

import * as Search from '../api/search';


const DEBOUNCE_INTERVAL = 500;


/**
 * Load the first page of search results, ensuring that requests are throttled.
 * Cached results are cleared.
 */
export function request({ query, suggestions = false })
{
    return (dispatch) =>
    {
        dispatch(getSearchAction(PENDING, query));
        execSearch(query, dispatch, suggestions);
    };
}

/**
 * Load the next page of search results for the given query. This is a no-op if the
 * query isn't the current one or if the search resource isn't in a success state.
 */
export function loadNextPage({ query })
{
    return (dispatch, getState) =>
    {
        const existing = getState().search.current;

        if (existing.status !== SUCCESS || existing.query !== query || existing.value.nextPage === null)
            return;

        dispatch(getSearchAction(PENDING, query));
        pending_state = getState().search.current;

        Search.loadPage(existing.value.nextPage).then(
            response => dispatch(getSearchAction(SUCCESS, query, { response })),
            error => dispatch(getSearchAction(ERROR, query, { error }))
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

const execSearch = debounce((query, dispatch, getSuggestions) =>
{
    if (!query)
    {
        dispatch(clear())
        return;
    }

    dispatch(searchAction(query));

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

const searchAction = (query) => 
{
    return (dispatch, getState) =>
    {
        let start_state = getState().search.current;
        Search.get(query).then(
            response =>
            {
                if (start_state.query === getState().search.current.query)
                    return dispatch(getSearchAction(SUCCESS, query, { response }));
            },
            error => dispatch(getSearchAction(ERROR, query, { error }))
        );
    }
}

/** Get a search status change action for the given status and query */
function getSearchAction(status, query, extra = null)
{
    return {
        type: SEARCH_REQUEST,
        payload: {
            ...extra,
            status,
            query
        }
    };
}


