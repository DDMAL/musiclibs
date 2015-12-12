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
        results = <span className="text-muted">{`Found ${pluralize(numFound, 'result')}.`}</span>;
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

/** Quick and dirty pluralization */
function pluralize(number, noun)
{
    switch (number)
    {
        case 0:
            return `no ${noun}s`;

        case 1:
            return `1 ${noun}`;

        default:
            return `${number} ${noun}s`;
    }
}

export default SearchResultsHeading;