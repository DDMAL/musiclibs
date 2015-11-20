import React, { PropTypes } from 'react';
import { connect } from 'react-redux';
import SearchInput from './search-input';
import { replaceState } from 'redux-react-router';
import { createSelector } from 'reselect';

import Resource from '../../resource-record';
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

        // Optional
        search: PropTypes.instanceOf(Resource),
        urlQuery: PropTypes.string
    };

    componentDidMount()
    {
        const { urlQuery, search } = this.props;

        if (!search || search.value.query !== urlQuery)
            this._loadQuery(urlQuery);
    }

    _loadQuery(query)
    {
        if (!query)
        {
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
        const query = this.props.urlQuery;

        let resultDisplay;

        if (query)
        {
            resultDisplay = (
                <SearchResults search={search} onLoadMore={() => this._loadMore(query)} />
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
