import React, { PropTypes } from 'react';
import Im from 'immutable';
import { Link } from 'react-router';

/** Suggest a correction for the query */
export default function SpellingSuggestion({ query, spellcheck })
{
    const correctionText = [];

    // Reconstruct the corrected query instead of using collationQuery because
    // it inserts backslashes before spaces
    let newQuery = '';
    let remaining = query.toLowerCase();

    for (const i of Im.Range(0, spellcheck.misspellingsAndCorrections.length, 2))
    {
        const [original, correction] = spellcheck.misspellingsAndCorrections.slice(i, i + 2);

        if (original === correction)
            continue;

        const originalStart = remaining.indexOf(original);

        // If we can't find the original and therefore build the corrected string, bail
        if (originalStart === -1)
        {
            console.error(`Failed to find misspelling ${original} in ...${remaining}`);
            return <noscript />;
        }

        const unchangedText = remaining.slice(0, originalStart);

        correctionText.push(unchangedText, <strong key={i}>{correction}</strong>);

        newQuery += unchangedText + correction;
        remaining = remaining.slice(originalStart + original.length);
    }

    if (remaining)
    {
        correctionText.push(remaining);
        newQuery += remaining;
    }

    // FIXME: Don't hardcode pathname
    return (
        <div className="text-muted">
            Showing results for <Link to={`/?q=${encodeURIComponent(newQuery)}`}>{correctionText}</Link>
        </div>
    );
}

SpellingSuggestion.propTypes = {
    query: PropTypes.string.isRequired,
    spellcheck: PropTypes.shape({
        misspellingsAndCorrections: PropTypes.arrayOf(PropTypes.string).isRequired,
        hits: PropTypes.number.isRequired,
        collationQuery: PropTypes.string.isRequired
    }).isRequired
};

