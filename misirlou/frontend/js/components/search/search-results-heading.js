import React, { PropTypes } from 'react';

import { ERROR, SUCCESS, PENDING } from '../../async-request-status';
import SearchResource from '../../resources/search-resource';

import SpellingSuggestion from './spelling-suggestion';
import SpellingCorrection from './spelling-correction';

/**
 * Display the number of results found and indicators of the current status
 */
function SearchResultsHeading({ status, searchResults, onRetry })
{
    let appliedCorrections;
    let spellcheck;
    let resultCount;
    let statusInfo;

    if (searchResults !== null)
    {
        resultCount = <span className="text-muted">{`Found ${pluralize(searchResults.numFound, 'result')}.`}</span>;
        if (searchResults.spellcheck)
            spellcheck = <SpellingSuggestion query={searchResults.query} spellcheck={searchResults.spellcheck} />;
        if (searchResults.appliedCorrection)
            appliedCorrections = <SpellingCorrection correction={searchResults.appliedCorrection} />;
    }

    if (status === PENDING)
    {
        statusInfo = <span className="text-muted">Loading...</span>;
    }
    else if (status === ERROR)
    {
        statusInfo = (
            <span className="text-danger">
                Failed to load results. {' '}
                <a href="#" onClick={onRetry}>
                    <strong className="text-danger">Retry.</strong>
                </a>
            </span>
        );
    }

    // Give empty divs if nothing is defined
    return (
        <div>
            {appliedCorrections}
            <div>{resultCount} {statusInfo}</div>
            {spellcheck}
        </div>
    );
}

SearchResultsHeading.propTypes = {
    status: PropTypes.oneOf([PENDING, ERROR, SUCCESS]).isRequired,

    // Optional
    searchResults: PropTypes.instanceOf(SearchResource.ValueClass),
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

