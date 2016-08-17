import React, { PropTypes } from 'react';
import { locationShape } from 'react-router';
import CSSTransitionGroup from 'react-addons-css-transition-group';

import updateSearch from './search-update-decorator';
import { request as searchRequest } from '../../action-creators/search';

@updateSearch
export default class SearchInput extends React.Component
{
    static propTypes = {
        // Optional
        className: PropTypes.string,

        // From updateSearch
        dispatch: PropTypes.func.dispatch,
        loadQuery: PropTypes.func.isRequired,
        loadPitchQuery: PropTypes.func.isRequired,
        query: PropTypes.string.isRequired,
        pitchQuery: PropTypes.string.isRequired,
        location: locationShape.isRequired,
        stats: PropTypes.shape({
            attributions: PropTypes.number.isRequired,
            manifests: PropTypes.number.isRequired
        }),
        suggestions: PropTypes.array
    };

    state = {
        pitchSearchShown: !!this.props.location.query.m
    };

    _onPitchBtnClick()
    {
        // Remove the pitch search terms if hiding the pitch search input
        if (this.state.pitchSearchShown)
        {
            const fakeEvent = { target: { value: '' } };
            this.props.loadPitchQuery(fakeEvent);
        }

        this.setState({ pitchSearchShown: !this.state.pitchSearchShown });
    }

    _getStatsDisplay()
    {
        let statDisplay;
        if (this.props.stats)
        {
            statDisplay = (
                <span className="text-muted">
                        Search {this.props.stats.manifests} documents from {this.props.stats.attributions} sources.
                </span>);
        }
        return statDisplay;
    }

    _onSuggestionClick = (event, suggestion) =>
    {
        event.preventDefault();
        this.changeSuggestionVisibility('hidden')();
        this.props.dispatch(searchRequest({
            query: suggestion,
            pitchQuery: this.props.pitchQuery,
            suggestions: true }));
    }

    _getSuggestionDisplay()
    {
        if (this.props.suggestions.length > 0)
        {
            const query = this.props.query;
            let rows = [];
            for (let i = 0, slen = this.props.suggestions.length; i < slen; i++)
            {
                let suggestion = this.props.suggestions[i];
                if (query.length)
                    suggestion = `${suggestion}`;
                rows.push(
                        <a href="#" key={i} data-key={i} data-suggestion={suggestion}
                            onMouseDown={(event) => this._onSuggestionClick(event, suggestion)}>
                                <div>{suggestion}</div></a>);
            }

            return (
                <div id="suggestions-dropdown">
                    {rows}
                </div>
            );
        }
    }

    suggestionIndex = -1;
    _onInputKeyUp()
    {
        let suggestionsDropdown = document.getElementById('suggestions-dropdown');
        if (!suggestionsDropdown)
            return () => undefined;

        return (e) =>
        {
            let suggestions = suggestionsDropdown.children;
            let refocus = () =>
            {
                for (let i = 0, slen = suggestions.length; i < slen; i++)
                {
                    if (suggestions[i].dataset.key == this.suggestionIndex) {
                        suggestions[i].className = "active";
                    } else {
                        suggestions[i].className = "";
                    }
                }
            };

            let slen = this.props.suggestions.length;
            switch(e.which) {
                //Down Key
                case 40:
                    this.suggestionIndex = (this.suggestionIndex + 1)%slen;
                    refocus();
                break;
                //Up Key
                case 38:
                    // n%m is in the range [-m+1, m-1] so adding m makes it strictly positive
                    this.suggestionIndex = (this.suggestionIndex%slen + slen - 1)%slen;
                    refocus();
                break;
                //Enter
                case 13:
                    let suggestions = suggestionsDropdown.children;
                    for (let i = 0; i < slen; i++)
                    {
                        if (suggestions[i].dataset.key == this.suggestionIndex)
                        {
                            this.props.dispatch(searchRequest({
                                query: suggestions[i].dataset.suggestion,
                                pitchQuery: this.props.pitchQuery,
                                suggestions: true }));
                        }
                    };
                    this.suggestionIndex = -1;
                break;
            };
        };
    }


    changeSuggestionVisibility(visibility)
    {
        return () =>
        {
            const suggestionsDropdown = document.getElementById('suggestionDropdown');
            if (suggestionsDropdown)
                suggestionsDropdown.style.visibility = visibility;
                this.suggestionIndex = -1;
        };
    }


    render()
    {
        const inputClass = this.state.pitchSearchShown ? '' : 'search-input__input--singular';
        const pitchBtnText = this.state.pitchSearchShown ? '<< Pitch Search (Experimental)' : '>> Pitch Search (Experimental)';

        return (
            <form onSubmit={e => e.preventDefault()} className={this.props.className}>
                <div className="search-input form-group">
                    <div>
                        <input type="search" name="q" placeholder="Search"
                               autoComplete="off"
                               className={`form-control search-input__input ${inputClass}`}
                               value={this.props.query}
                               onChange={this.props.loadQuery}
                               onFocus={this.changeSuggestionVisibility('visible')}
                               onKeyUp={(event) => this._onInputKeyUp()(event)}
                               onBlur={this.changeSuggestionVisibility('hidden')}/>
                        <CSSTransitionGroup transitionName="input-anim"
                                            transitionEnterTimeout={200}
                                            transitionLeaveTimeout={200}>
                            {this.state.pitchSearchShown && (
                                <input type="search" name="m" placeholder="Pitch Search"
                                       className="form-control search-input__input"
                                       value={this.props.pitchQuery}
                                       onChange={this.props.loadPitchQuery}/>
                            )}
                        </CSSTransitionGroup>
                        <div id="suggestionDropdown">
                            {this._getSuggestionDisplay()}
                        </div>
                    </div>
                    <div className="row">
                        <div className="col-xs-6" style={{ textAlign: 'left', paddingRight: '0' }}>
                            <span className="search-input__stat-display">{this._getStatsDisplay()}</span>
                        </div>
                        <div className="col-xs-6" style={{ textAlign: 'right', paddingLeft: '0' }}>
                            <CSSTransitionGroup transitionName="pitchBtn-anim"
                                                transitionEnterTimeout={200}
                                                transitionLeaveTimeout={10}>
                                {/* Use a key to create a new label every time the pitch input is shown.
                                    That way the animation always triggers */}
                                <label key={inputClass} className="search-input__pitch-btn" onClick={() => this._onPitchBtnClick()}>
                                    {pitchBtnText}
                                </label>
                            </CSSTransitionGroup>
                        </div>
                    </div>
                </div>
            </form>
        );
    }
}
