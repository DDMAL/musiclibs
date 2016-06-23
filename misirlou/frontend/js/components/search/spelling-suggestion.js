import React, { PropTypes } from 'react';
import Im from 'immutable';
import {request as searchRequest} from '../../action-creators/search';
import { connect } from 'react-redux';
import { createSelector } from 'reselect';

const getState = createSelector(
    ({ search }) => search,
    (search) => ({ pitchQuery: search.current.pitchQuery })
);

/** Suggest a correction for the query */
@connect(getState)
export default class SpellingSuggestion extends React.Component
{
    static propTypes = {
        dispatch: PropTypes.func.isRequired,
        query: PropTypes.string.isRequired,
        pitchQuery: PropTypes.string.isRequired,
        spellcheck: PropTypes.shape({
            misspellingsAndCorrections: PropTypes.arrayOf(PropTypes.string).isRequired,
            hits: PropTypes.number.isRequired,
            collationQuery: PropTypes.string.isRequired
        }).isRequired
    };

    onClick(event, val)
    {
        event.preventDefault();
        this.props.dispatch(searchRequest({
            query: val,
            pitchQuery: this.props.pitchQuery,
            suggestions: true }));
    }

    render()
    {
        const correctionText = [];

        // Reconstruct the corrected query instead of using collationQuery because
        // it inserts backslashes before spaces
        let newQuery = '';
        let remaining = this.props.query.toLowerCase();
        const spellcheck = this.props.spellcheck;

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

        return (
            <div className="text-muted">
                Did you mean <a href="#" onClick={event =>
                this.onClick(event, newQuery)}>{correctionText}</a>?
            </div>
        );
    }
}
