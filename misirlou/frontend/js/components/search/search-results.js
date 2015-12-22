import React, { PropTypes } from 'react';

import SearchResource from '../../resources/search-resource';

import SearchResultsHeading from './search-results-heading';
import SearchResultItem from './search-result-item';
import FollowupActions from './followup-actions';

/** Show a list of results, or an appropriate loading or error state */
function SearchResults({ search, onLoadMore, onRetry })
{
    // No current search; nothing to show
    if (search.current.query === null)
        return <noscript/>;

    let results;
    let followup;

    if (search.current.value !== null)
    {
        results = search.current.value.results;

        if (results.size > 0)
        {
            followup = (
                <FollowupActions resource={search.current} onLoadMore={onLoadMore} onRetry={onRetry} />
            );
        }
    }
    else if (search.stale.value !== null)
    {
        // Display stale results if the current results aren't ready
        results = search.stale.value.results;
    }

    return (
        <div>
            <SearchResultsHeading
                status={search.current.status}
                searchResults={search.current.value}
                onRetry={onRetry} />

            {results ?
                results.toSeq()
                    .map((result, i) => <SearchResultItem key={i} result={result} />)
                    .toArray() :
                null}

            {followup}
        </div>
    );
}

SearchResults.propTypes = {
    search: PropTypes.shape({
        current: PropTypes.instanceOf(SearchResource).isRequired,
        stale: PropTypes.instanceOf(SearchResource).isRequired
    }).isRequired,

    // Optional
    onLoadMore: PropTypes.func,
    onRetry: PropTypes.func
};

export default SearchResults;
