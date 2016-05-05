import React, { PropTypes } from 'react';
import { connect } from 'react-redux';
import { withRouter, locationShape, routerShape } from 'react-router';
import { createSelector } from 'reselect';

import SearchResource from '../../resources/search-resource';
import * as Search from '../../action-creators/search';

import SearchInput from './search-input';
import SearchResults from './search-results';


/* State selectors */

const getState = createSelector(
    ({ search }) => search,
    search => ({ search })
);


/* Components */

@withRouter
@connect(getState)
export default class SearchContainer extends React.Component
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
        this._currentQuery = this.props.search.current.query;
        const urlQuery = getQueryFromLocation(this.props.location);

        if (this._currentQuery !== urlQuery)
            this._loadQuery(urlQuery);
    }

    componentWillReceiveProps(next)
    {
        const nextCurrentQuery = next.search.current.query;

        if (nextCurrentQuery !== this._currentQuery)
        {
            this._currentQuery = nextCurrentQuery;
            const routerQuery = nextCurrentQuery ? { query: nextCurrentQuery } : {};

            this.props.router.replace({
                ...this.props.location,
                query: routerQuery
            });

            return;
        }

        const priorLocationQuery = getQueryFromLocation(this.props.location);
        const nextLocationQuery = getQueryFromLocation(next.location);

        if (nextLocationQuery !== priorLocationQuery && nextLocationQuery !== this._currentQuery)
            this._loadQuery(nextLocationQuery);
    }

    componentWillUnmount()
    {
        if (this.props.search.current.query)
            this.props.dispatch(Search.clear());
    }

    _loadQuery(query)
    {
        this._currentQuery = query || null;

        if (!query)
        {
            this.props.dispatch(Search.clear());
            return;
        }

        this.props.dispatch(Search.request({
            query,
            suggestions: true
        }));
    }

    _loadMore(query)
    {
        this.props.dispatch(Search.loadNextPage({ query }));
    }

    render()
    {
        const search = this.props.search;
        const query = search.current.query;

        let resultDisplay;

        if (query)
        {
            resultDisplay = (
                <SearchResults search={search}
                               onLoadMore={() => this._loadMore(query)}
                               onRetry={() => this._loadQuery(query)} />
            );
        }

        return (
            <div>
                <SearchInput
                        inputClasses="input-lg"
                        query={query}
                        onChange={({ target: { value } }) => this._loadQuery(value)} />
                {resultDisplay}
            </div>
        );
    }
}

function getQueryFromLocation(loc)
{
    return loc.query.q || null;
}
