import debounce from 'lodash.debounce';

import { PENDING, ERROR, SUCCESS } from '../async-request-status';
import { SEARCH_REQUEST_STATUS_CHANGE, CLEAR_SEARCH } from '../actions';

import * as Search from '../api/search';


const DEBOUNCE_INTERVAL = 500;


/**
 * Load the first page of search results, ensuring that requests are throttled.
 * Cached results are cleared.
 */
export function request({ query })
{
    return (dispatch, getState) =>
    {
        dispatch(getSearchAction(PENDING, query));
        execRequest(query, dispatch, getState);
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

        if (existing.status !== SUCCESS || existing.query !== query || existing.nextPage === null)
            return;

        dispatch(getSearchAction(PENDING, query));

        Search.loadPage(existing.nextPage).then(
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

const execRequest = debounce((query, dispatch) =>
{
    Search.get(query).then(
        response => dispatch(getSearchAction(SUCCESS, query, { response })),
        error => dispatch(getSearchAction(ERROR, query, { error }))
    );
}, DEBOUNCE_INTERVAL);

/** Get a search status change action for the given status and query */
function getSearchAction(status, query, extra = null)
{
    return {
        type: SEARCH_REQUEST_STATUS_CHANGE,
        payload: {
            ...extra,
            status,
            query
        }
    };
}
