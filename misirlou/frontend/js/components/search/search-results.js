import React, { PropTypes } from 'react';
import { Link } from 'react-router';

import { ERROR, SUCCESS } from '../../async-status-record';
import Resource from '../../resource-record';


/** Show a list of results, or an appropriate loading or error state */
function SearchResults({ search, onLoadMore })
{
    return (
        <div>
            <SearchResultList search={search} />
            <SearchStatusMessage search={search} onLoadMore={onLoadMore} />
        </div>
    );
}

SearchResults.propTypes = {
    // Optional
    search: PropTypes.instanceOf(Resource),
    onLoadMore: PropTypes.func
};

/** Display a listing of search results */
export function SearchResultList({ search })
{
    let resultArray;

    if (!search)
    {
        resultArray = [];
    }
    else
    { // eslint-disable-line space-after-keywords
        resultArray = search.value.results.toSeq()
            .map((result, i) => <SearchResultItem key={i} result={result} />)
            .toArray();
    }

    return <div>{resultArray}</div>;
}

SearchResultList.propTypes = {
    // Optional
    search: PropTypes.instanceOf(Resource)
};

/** Display basic information for a search result, linking to the full manifest */
export function SearchResultItem({ result })
{
    return <p><Link to={`/manifests/${result.id}/`}>{result.label}</Link></p>;
}

SearchResultItem.propTypes = {
    result: PropTypes.shape({
        id: PropTypes.string.isRequired,

        label: PropTypes.oneOfType([
            PropTypes.string,
            PropTypes.arrayOf(PropTypes.string)
        ]).isRequired
    })
};

/** Display actions/indicators of search state */
export function SearchStatusMessage({ search, onLoadMore })
{
    switch (search && search.status)
    {
        case SUCCESS:
            if (search.value.nextPage)
            {
                return (
                    <div>
                        <button className="btn btn-default" onClick={onLoadMore}>Load more</button>
                    </div>
                );
            }

            return <div />;

        case ERROR:
            return (
                <p className="alert alert-danger">
                    :(
                </p>
            );

        default:
            // Show a loading label event if there is no response to prevent
            // flickering
            return (
                <p>Loading...</p>
            );
    }
}

SearchStatusMessage.propTypes = {
    // Optional
    search: PropTypes.instanceOf(Resource),
    onLoadMore: PropTypes.func
};

export default SearchResults;
