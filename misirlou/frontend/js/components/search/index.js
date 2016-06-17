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
    ({ stats }) => stats,
    (search, stats) => ({ search, stats })
);

/* Components */

@connect(getState)
export default class SearchContainer extends React.Component
{
    static propTypes = {
        search: PropTypes.shape({
            current: PropTypes.instanceOf(SearchResource).isRequired,
            stale: PropTypes.instanceOf(SearchResource).isRequired
        }).isRequired,
        location: locationShape.isRequired,
        stats: PropTypes.shape({
            attributions: PropTypes.number.isRequired,
            manifests: PropTypes.number.isRequired
        })
    };

    render()
    {
        const { search } = this.props;
        const { stats } = this.props;
        const { location } = this.props;
        const query = search.current.query;

        let resultDisplay;
        let statDisplay;

        if (query)
        {
            resultDisplay = (
                <SearchResults location={location}
                               onLoadMore={() => this._loadMore(query)}
                               onRetry={() => this._loadQuery(query)} />
            );
        }
        else if (stats !== null)
        {
            statDisplay = (
                <span className="text-muted">
                    Search {stats.manifests} documents from {stats.attributions} sources.
                </span>);
        }

        return (
            <div>
                <SearchInput location={location}
                        inputClasses="input-lg" />
                {statDisplay}
                {resultDisplay}
            </div>
        );
    }
}
