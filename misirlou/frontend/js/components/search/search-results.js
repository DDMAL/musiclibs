import React, { PropTypes } from 'react';

import SearchResource from '../../resources/search-resource';
import updateSearch from './search-update-decorator';
import SearchResultsHeading from './search-results-heading';
import SearchResultItem from './result-item/index';
import FollowupActions from './followup-actions';


/** Show a list of results, or an appropriate loading or error state */
@updateSearch
export default class SearchResults extends React.Component
{
    static propTypes = {
        // From updateSearch
        loadQuery: PropTypes.func.isRequired,
        loadMore: PropTypes.func.isRequired,
        retry: PropTypes.func.isRequired,
        search: PropTypes.shape({
            current: PropTypes.instanceOf(SearchResource).isRequired,
            stale: PropTypes.instanceOf(SearchResource).isRequired
        }).isRequired
    };

    static contextTypes = {
        router: PropTypes.object.isRequired
    }

    render()
    {
        const { search } = this.props;
        const query = search.current.query;

        // No current search; nothing to show
        if (query === null)
            return <noscript />;

        let results;
        let followup;

        if (search.current.value !== null)
        {
            results = search.current.value.results;

            if (results.size > 0)
            {
                followup = (
                    <FollowupActions resource={search.current}
                                     onLoadMore={this.props.loadMore} />
                );
            }
        }
        else if (search.stale.value !== null)
        {
            // Display stale results if the current results aren't ready
            results = search.stale.value.results;
        }
        else
            return <noscript />; // Search has not started yet

        return (
            <div className="search-results">
                <SearchResultsHeading
                    status={search.current.status}
                    searchResults={search.current.value}
                    onRetry={this.props.retry} />

                {results ?
                    results.toSeq()
                        .map((result, i) => <SearchResultItem key={i} result={result}
                                                              query={search.current.query}
                                                              pitchQuery={search.current.pitchQuery}/>)
                        .toArray() :
                    null}

                {(results.size === 1 &&
                    this.props.location.pathname !== '/manifests/' + results.toArray()[0].local_id) ?
                    this.context.router.push({
                        pathname: '/manifests/' + results.toArray()[0].local_id,
                        query: {q: search.current.query}
                    }) : null}

                {followup}
            </div>
        );
    }
}
