import React, { PropTypes } from 'react';
import { Link } from 'react-router';

import AsyncStatusRecord, { ERROR, SUCCESS } from '../../async-status-record';


/** Show a list of results, or an appropriate loading or error state */
function SearchResults({ response, onLoadMore })
{
    return (
        <div>
            <SearchResultList response={response} />
            <SearchStatusMessage response={response} onLoadMore={onLoadMore} />
        </div>
    );
}

SearchResults.propTypes = {
    // Optional
    response: PropTypes.objectOf(AsyncStatusRecord),
    onLoadMore: PropTypes.func
};

/** Display a listing of search results */
export function SearchResultList({ response })
{
    let resultArray;

    if (!response || !response.value)
    {
        resultArray = [];
    }
    else
    { // eslint-disable-line space-after-keywords
        resultArray = response.value.results.toSeq()
            .map((result, i) => <SearchResultItem key={i} result={result} />)
            .toArray();
    }

    return <div>{resultArray}</div>;
}

SearchResultList.propTypes = {
    // Optional
    response: PropTypes.objectOf(AsyncStatusRecord)
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
export function SearchStatusMessage({ response, onLoadMore })
{
    switch (response && response.status)
    {
        case SUCCESS:
            if (response.value.nextPage)
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
    response: PropTypes.objectOf(AsyncStatusRecord),
    onLoadMore: PropTypes.func
};

export default SearchResults;
