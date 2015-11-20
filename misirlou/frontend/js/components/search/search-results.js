import React, { PropTypes } from 'react';
import Im from 'immutable';
import { Link } from 'react-router';

import { ERROR, SUCCESS, PROCESSING } from '../../async-status-record';
import Resource from '../../resource-record';


/** Show a list of results, or an appropriate loading or error state */
function SearchResults({ search, onLoadMore })
{
    let numFound;

    if (search && search.status !== PROCESSING)
    {
        let text;

        switch (search.value.numFound)
        {
            case 0:
                text = 'Found no results';
                break;

            case 1:
                text = 'Found 1 result';
                break;

            default:
                text = `Found ${search.value.numFound} results`;
        }

        numFound = <p className="text-muted">{text}</p>;
    }

    return (
        <div>
            {numFound}
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
    const listing = Im.Seq(hits)
    .filter(hit => hit.field.indexOf('_') === -1)
    .map((hit, i) => (
        [
            <dt key={`t-${i}`}>{hit.field.charAt(0).toUpperCase() + hit.field.slice(1)}</dt>,
            <dd key={`d-${i}`}>{hit.parsed.map((text, i) => (
                i % 2 === 0 ? <span key={i}>{text}</span> : <mark key={i}>{text}</mark>
            ))}</dd>
        ]
    ))
    .flatten(true)
    .toArray();

    if (listing.length === 0)
        return <div/>;

    return (
        <dl style={{ paddingLeft: 20 }}>{listing}</dl>
    );
}

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
                        <button className="btn btn-default center-block" onClick={onLoadMore}>Load more</button>
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
