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
    ({ stats }) => stats,
    (search, stats) => ({
        search,
        stats,
        query: search.current.query,
        pitchQuery: search.current.pitchQuery,
        suggestions: search.current.suggestions.toArray()
    })
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
        query: PropTypes.string.isRequired,
        pitchQuery: PropTypes.string.isRequired,
        location: locationShape.isRequired,
        router: routerShape.isRequired,
        stats: PropTypes.shape({
            attributions: PropTypes.number.isRequired,
            manifests: PropTypes.number.isRequired
        }),
        suggestions: PropTypes.array
    };

    // Load the query from the URL
    componentDidMount()
    {
        const urlQuery = getQueryFromLocation(this.props.location);

        if (this.props.query !== urlQuery.query
            || this.props.pitchQuery !== urlQuery.pitchQuery)
        {
            this._loadQuery(urlQuery.query, urlQuery.pitchQuery);
        }

        this.props.dispatch(Search.getStats());
    }

    componentWillReceiveProps(next)
    {
        if (next.query !== this.props.query || next.pitchQuery !== this.props.pitchQuery)
        {
            this.props.router.replace({
                ...this.props.location,
                query: this._parseQuery(next.query, next.pitchQuery),
                state: {
                    searchQueryHandled: true
                }
            });
        }
    }
    _parseQuery(nextQuery, nextPitchQuery)
    {
        const oldQuery = this.props.location.query;
        if (nextQuery)
            oldQuery.q = nextQuery;
        else
            delete oldQuery.q;

        if (nextPitchQuery)
            oldQuery.m = nextPitchQuery;
        else
            delete oldQuery.m;

        return oldQuery;
    }

    componentWillUnmount()
    {
        if (this.props.query)
            this.props.dispatch(Search.clear());
    }

    _loadQuery(query, pitchQuery, forceLoad = false)
    {
        // Usually, one of the two args will be null since only one field has been updated
        if (query === null)
            query = this.props.query;
        if (pitchQuery === null)
            pitchQuery = this.props.pitchQuery;

        if (forceLoad || query !== this.props.query || pitchQuery !== this.props.pitchQuery)
        {
            this.props.dispatch(Search.request({
                query,
                pitchQuery,
                suggestions: true
            }));
        }
    }

    _loadMore(query, pitchQuery)
    {
        this.props.dispatch(Search.loadNextPage({ query, pitchQuery }));
    }

    render()
    {
        const query = this.props.query;
        const pitchQuery = this.props.pitchQuery;
        return (
            <ComposedComponent {...this.props}
            loadQuery={({ target: { value } }) => this._loadQuery(value, null)}
            loadPitchQuery={({ target: { value } }) => this._loadQuery(null, value)}
            loadMore={() => this._loadMore(query, pitchQuery)}
            retry={() => this._loadQuery(query, pitchQuery, true)}/>
        );
    }
};

function getQueryFromLocation(loc)
{
    return {
        query: loc.query.q || '',
        pitchQuery: loc.query.m || ''
    };
}
