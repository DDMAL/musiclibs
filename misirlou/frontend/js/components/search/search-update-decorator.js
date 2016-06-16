import React, { PropTypes } from 'react';
import { createSelector } from 'reselect';
import { connect } from 'react-redux';
import { withRouter, locationShape, routerShape } from 'react-router';

import SearchResource from '../../resources/search-resource';
import * as Search from '../../action-creators/search';


/**
 * This is a component used by both the search-results
 * and the search-input. It extracts the features of
 * url updating and search querying in order to be able
 * to use the two components mentioned above individually
 * and to be able to have them separated (no common parent)
 *
 * To use it:
 *
 * As a decorator:
 * >>> import updateSearch from 'path-to-this-file';
 * >>> @updateSearch
 * >>> class MyComponent extends React.Component
 *
 * OR:
 * >>> updateSearch(MyComponent)
 * where MyComponent is a class inheriting from React.Component
 *
 * The idea comes from this gist:
 * https://gist.github.com/sebmarkbage/ef0bf1f338a7182b6775
 * Also checkout my fork adapted for ES7:
 * https://gist.github.com/jeromepl/2f7df563f273563261690221c22aa0af
 *
 * Note that this could have been implemented using mixins
 * (https://facebook.github.io/react/docs/reusable-components.html#mixins)
 * but this newer method was preferred since React is moving
 * away from mixins.
 */

const getState = createSelector(
    ({ search }) => search,
    (search) => ({ search })
);

@withRouter
@connect(getState)
export default (ComposedComponent) => class extends React.Component
{
    static propTypes = {
        dispatch: PropTypes.func.isRequired,
        search: PropTypes.shape({
            current: PropTypes.instanceOf(SearchResource).isRequired,
            stale: PropTypes.instanceOf(SearchResource).isRequired
        }).isRequired,
        location: locationShape.isRequired,
        router: routerShape.isRequired
    };

    // Load the query from the URL
    componentDidMount()
    {
        const urlQuery = getQueryFromLocation(this.props.location);

        if (this.props.search.current.query !== urlQuery.query
            || this.props.search.current.pitchQuery !== urlQuery.pitchQuery)
        {
            this._loadQuery(urlQuery.query, urlQuery.pitchQuery);
        }

        this.props.dispatch(Search.getStats());
    }

    componentWillReceiveProps(next)
    {
        const nextQuery = next.search.current.query;
        const nextPitchQuery = next.search.current.pitchQuery;

        if (nextQuery !== this.props.search.current.query || nextPitchQuery !== this.props.search.current.pitchQuery)
        {
            let routerQuery = nextQuery ? { q: nextQuery } : {};

            if (nextPitchQuery)
                routerQuery.m = nextPitchQuery;

            this.props.router.replace({
                ...this.props.location,
                query: routerQuery,
                state: {
                    searchQueryHandled: true
                }
            });

            return;
        }

        const priorLocQuery = getQueryFromLocation(this.props.location);
        const nextLocQuery = getQueryFromLocation(next.location);
        const nextLocState = next.location.state;

        if ((nextLocQuery.query !== priorLocQuery.query || nextLocQuery.pitchQuery !== priorLocQuery.pitchQuery)
            && !(nextLocState && nextLocState.searchQueryHandled))
            this._loadQuery(nextLocQuery.query, nextLocQuery.pitchQuery);
    }

    componentWillUnmount()
    {
        if (this.props.search.current.query)
            this.props.dispatch(Search.clear());
    }

    _loadQuery(query, pitchQuery)
    {
        // Usually, one of the two args will be null since only one field has been updated
        if (query === null)
            query = this.props.search.current.query;
        if (pitchQuery === null)
            pitchQuery = this.props.search.current.pitchQuery;

        if (!query && !pitchQuery)
        {
            this.props.dispatch(Search.clear());
            return;
        }

        this.props.dispatch(Search.request({
            query,
            pitchQuery,
            suggestions: true
        }));
    }

    _loadMore(query)
    {
        this.props.dispatch(Search.loadNextPage({ query }));
    }

    render()
    {
        const query = this.props.search.current.query;
        return <ComposedComponent {...this.props}
            loadQuery={({ target: { value } }) => this._loadQuery(value, null)}
            loadPitchQuery={({ target: { value } }) => this._loadQuery(null, value)}
            loadMore={() => this._loadMore(query)} />
    }
}

function getQueryFromLocation(loc)
{
    return {
            query: loc.query.q || '',
            pitchQuery: loc.query.m || ''
        };
}
