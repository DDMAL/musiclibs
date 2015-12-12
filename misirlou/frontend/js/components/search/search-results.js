import React, { PropTypes } from 'react';
import Im from 'immutable';
import { Link } from 'react-router';

import { ERROR, SUCCESS, PROCESSING } from '../../async-status-record';
import SearchResource from '../../resources/search-resource';
import DescriptionList from '../ui/description-list';
import ErrorAlert from '../ui/error-alert';


/** Show a list of results, or an appropriate loading or error state */
function SearchResults({ search, onLoadMore, onRetry })
{
    return (
        <div>
            <SearchResultHeading search={search} onRetry={onRetry} />
            <SearchResultList search={search} onLoadMore={onLoadMore} onRetry={onRetry} />
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

/** Display the search result status */
function SearchResultHeading({ search, onRetry })
{
    // Nothing to see here
    if (search.current.query === null)
        return <noscript/>;

    let results;
    let status;

    if (search.current.numFound !== null)
    {
        let text;

        switch (search.current.numFound)
        {
            case 0:
                text = 'Found no results.';
                break;

            case 1:
                text = 'Found 1 result.';
                break;

            default:
                text = `Found ${search.current.numFound} results.`;
        }

        results = <span className="text-muted">{text}</span>;
    }

    if (search.current.status === PROCESSING)
    {
        status = <span className="text-muted">Loading...</span>;
    }
    else if (search.current.status === ERROR)
    {
        status = (
            <span className="text-danger">
                Failed to load results.
                <button type="button" className="btn btn-link text-danger" onClick={onRetry}>
                    <strong className="text-danger">Retry.</strong>
                </button>
            </span>
        );
    }

    if (results || status)
        return <p>{results} {status}</p>;

    return <noscript/>;
}

SearchResultHeading.propTypes = {
    search: PropTypes.shape({
        current: PropTypes.instanceOf(SearchResource).isRequired,
        stale: PropTypes.instanceOf(SearchResource).isRequired
    }).isRequired,

    // Optional
    onRetry: PropTypes.func
};

/** Display a listing of search results */
export function SearchResultList({ search, onLoadMore, onRetry })
{
    let results;
    let resultArray;
    let followup;

    if (search.current.numFound !== null)
    {
        results = search.current.results;

        if (results.size > 0)
        {
            followup = (
                <SearchFollowupActions search={search} onLoadMore={onLoadMore} onRetry={onRetry} />
            );
        }
    }
    else if (search.current.status === PROCESSING && search.stale.numFound !== null)
        results = search.stale.results;

    if (results)
    {
        resultArray = results.toSeq()
            .map((result, i) => <SearchResultItem key={i} result={result} />)
            .toArray();
    }

    return (
        <div>
            {resultArray}
            {followup}
        </div>
    );
}

SearchResultList.propTypes = {
    search: PropTypes.shape({
        current: PropTypes.instanceOf(SearchResource).isRequired,
        stale: PropTypes.instanceOf(SearchResource).isRequired
    }).isRequired,

    // Optional
    onLoadMore: PropTypes.func,
    onRetry: PropTypes.func
};

/** Display basic information for a search result, linking to the full manifest */
export function SearchResultItem({ result })
{
    return (
        <div>
            <h2 className="h3"><Link to={`/manifests/${result.id}/`}>{result.label}</Link></h2>
            <HitList hits={result.hits} />
            {result.description ? <p>{result.description}</p> : null}
        </div>
    );
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

/** Display a list of hits */
export function HitList({ hits })
{
    const terms = Im.Seq(hits)
        .filter(hit => hit.field !== 'metadata' && hit.field.indexOf('_') === -1)
        .map((hit, i) => ({
            term: hit.field.charAt(0).toUpperCase() + hit.field.slice(1),
            description: hit.parsed.map((text, i) => (
                i % 2 === 0 ? <span key={i}>{text}</span> : <mark key={i}>{text}</mark>
            ))
        }))
        .toArray();

    if (terms.length === 0)
        return <noscript />;

    return <DescriptionList style={{ marginLeft: 20 }} terms={terms} />;
}

HitList.propTypes = {
    hits: PropTypes.objectOf(Im.List)
};

/** Display follow-up actions */
export function SearchFollowupActions({ search, onLoadMore, onRetry })
{
    switch (search.current.status)
    {
        case SUCCESS:
            if (!search.current.nextPage)
            {
                // Nothing to do
                return <noscript />;
            }

            return (
                <div>
                    <button className="btn btn-default center-block" onClick={onLoadMore}>Load more</button>
                </div>
            );

        case ERROR:
            return (
                <ErrorAlert title="Search failed">
                    <button className="btn btn-default center-block" onClick={onRetry}>Retry</button>
                </ErrorAlert>
            );

        case PROCESSING:
            // Demonstrate that we're loading more results
            return (
                <div>
                    <button className="btn btn-default center-block" disabled={true}>Loading...</button>
                </div>
            );
    }
}

SearchFollowupActions.propTypes = {
    search: PropTypes.shape({
        current: PropTypes.instanceOf(SearchResource).isRequired,
        stale: PropTypes.instanceOf(SearchResource).isRequired
    }).isRequired,

    // Optional
    onLoadMore: PropTypes.func,
    onRetry: PropTypes.func
};

export default SearchResults;
