import React, { PropTypes } from 'react';
import { connect } from 'react-redux';
import { locationShape } from 'react-router';
import { createSelector } from 'reselect';

import SearchInput from './search-input';
import SearchResults from './search-results';


/* State selectors */

const getState = createSelector(
    ({ search }) => search,
    ({ stats }) => stats,
    (search, stats) => ({
        query: search.current ? search.current.query : null,
        stats
    })
);

/* Components */

@connect(getState)
export default class SearchContainer extends React.Component
{
    static propTypes = {
        query: PropTypes.string.isRequired,
        location: locationShape.isRequired,
        stats: PropTypes.shape({
            attributions: PropTypes.number.isRequired,
            manifests: PropTypes.number.isRequired
        })
    };

    render()
    {
        const { stats } = this.props;
        const { location } = this.props;
        const query = this.props.query;

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
