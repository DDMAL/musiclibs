import React, { PropTypes } from 'react';
import { connect } from 'react-redux';
import SearchInput from './search-input';
import { replaceState } from 'redux-react-router';
import { createSelector } from 'reselect';

import SearchResource from '../../resources/search-resource';
import * as Search from '../../action-creators/search';

import SearchResults from './search-results';


/* State selectors */

const getState = createSelector(
    state => state.search,
    state => state.router.location.query.q,
    state => state.router.location.pathname,
    (search, urlQuery, pathname) => ({ search, urlQuery, pathname })
);


/* Components */

@connect(getState)
export default class SearchPageContainer extends React.Component
{
    static propTypes = {
        dispatch: PropTypes.func.isRequired,
        pathname: PropTypes.string.isRequired,
        search: PropTypes.shape({
            current: PropTypes.instanceOf(SearchResource).isRequired,
            stale: PropTypes.instanceOf(SearchResource).isRequired
        }).isRequired,

        // Optional
        urlQuery: PropTypes.string
    };

    componentDidMount()
    {
        const { urlQuery, search } = this.props;

        if (search.current.query !== urlQuery)
            this._loadQuery(urlQuery);
    }

    componentWillUnmount()
    {
        this.props.dispatch(Search.clear());
    }

    _loadQuery(query)
    {
        if (!query)
        {
            this.props.dispatch(Search.clear());
            this.props.dispatch(replaceState(null, this.props.pathname));
            return;
        }

        this.props.dispatch(replaceState(null, this.props.pathname, {
            q: query
        }));

        this.props.dispatch(Search.request({ query }));
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
            <div className="container">
                <header className="page-header">
                    <h1>Search</h1>
                </header>
                <SearchInput
                        query={query}
                        onChange={({ target: { value } }) => this._loadQuery(value)} />
                {resultDisplay}
            </div>
        );
    }
}

export const __hotReload = true;
