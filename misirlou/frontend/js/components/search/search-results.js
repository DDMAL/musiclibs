import React, { PropTypes } from 'react';
import { Link } from 'react-router';

import AsyncStatusRecord, { PROCESSING, ERROR, SUCCESS } from '../../async-status-record';


/** Show a list of results, or an appropriate loading or error state */
function SearchResultList({ query, results })
{
    switch (results && results.status)
    {
        case SUCCESS:
            if (results.value.size === 0)
            {
                return <p>No results</p>;
            }

            const resultArray = results.value.toSeq()
                .map((result, i) => <SearchResult key={i} result={result} />)
                .toArray();

            return (
                <div>{resultArray}</div>
            );

        case ERROR:
            return (
                <p className="alert alert-danger">
                    :(
                </p>
            );

        default:
            // Show the loading value if there's a query but no result record
            // to stop the loading indicator from flickering as a new query
            // is typed

            if (!query)
                return <div />;

        // fallthrough

        case PROCESSING:
            return <p>Loading...</p>;
    }
}

SearchResultList.propTypes = {
    // Optional
    results: PropTypes.objectOf(AsyncStatusRecord),
    query: PropTypes.string
};


/** Display basic information for a search result, linking to the full manifest */
export function SearchResult({ result })
{
    return <p><Link to={`/manifests/${result.id}/`}>{result.label}</Link></p>;
}

SearchResult.propTypes = {
    result: PropTypes.shape({
        // FIXME this should become uuid or something
        id: PropTypes.string.isRequired,

        label: PropTypes.oneOfType([
            PropTypes.string,
            PropTypes.arrayOf(PropTypes.string)
        ]).isRequired
    })
};

export default SearchResultList;
