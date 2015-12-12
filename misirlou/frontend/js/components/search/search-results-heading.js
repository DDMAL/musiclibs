import React, { PropTypes } from 'react';

import { ERROR, SUCCESS, PROCESSING } from '../../async-status-record';

/**
 * Display the number of results found and indicators of the current status
 */
function SearchResultsHeading({ status, numFound, onRetry })
{
    let results;
    let statusInfo;

    if (numFound !== null)
    {
        let text;

        switch (numFound)
        {
            case 0:
                text = 'Found no results.';
                break;

            case 1:
                text = 'Found 1 result.';
                break;

            default:
                text = `Found ${numFound} results.`;
        }

        results = <span className="text-muted">{text}</span>;
    }

    if (status === PROCESSING)
    {
        statusInfo = <span className="text-muted">Loading...</span>;
    }
    else if (status === ERROR)
    {
        statusInfo = (
            <span className="text-danger">
                Failed to load results.
                <a href="#" onClick={onRetry}>
                    <strong className="text-danger">{' Retry.'}</strong>
                </a>
            </span>
        );
    }

    if (results || statusInfo)
        return <p>{results} {statusInfo}</p>;

    return <noscript/>;
}

SearchResultsHeading.propTypes = {
    status: PropTypes.oneOf([PROCESSING, ERROR, SUCCESS]).isRequired,

    // Optional
    numFound: PropTypes.number,
    onRetry: PropTypes.func
};

export default SearchResultsHeading;