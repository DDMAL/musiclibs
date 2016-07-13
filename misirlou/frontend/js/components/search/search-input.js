import React, { PropTypes } from 'react';
import { locationShape } from 'react-router';
import CSSTransitionGroup from 'react-addons-css-transition-group';

import SearchResource from '../../resources/search-resource';
import updateSearch from './search-update-decorator';

@updateSearch
export default class SearchInput extends React.Component
{
    static propTypes = {
        // Optional
        className: PropTypes.string,

        // From updateSearch
        loadQuery: PropTypes.func.isRequired,
        loadPitchQuery: PropTypes.func.isRequired,
        query: PropTypes.string.isRequired,
        pitchQuery: PropTypes.string.isRequired,
        location: locationShape.isRequired,
        stats: PropTypes.shape({
            attributions: PropTypes.number.isRequired,
            manifests: PropTypes.number.isRequired
        })
    };

    state = {
        pitchSearchShown: this.props.location.query.m ? true : false
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
                        Search {this.props.stats.manifests} documents from {this.props.stats.attributions} libraries.
                </span>);
        }
        return statDisplay
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
                               className={`form-control search-input__input ${inputClass}`}
                               value={this.props.query}
                               onChange={this.props.loadQuery} />
                        <CSSTransitionGroup transitionName="input-anim"
                                            transitionEnterTimeout={200}
                                            transitionLeaveTimeout={200}>
                            {this.state.pitchSearchShown && (
                                <input type="search" name="m" placeholder="Pitch Search"
                                       className='form-control search-input__input'
                                       value={this.props.pitchQuery}
                                       onChange={this.props.loadPitchQuery}/>
                            )}
                        </CSSTransitionGroup>
                    </div>
                    <div className="row">
                        <div className="col-xs-6" style={{textAlign: "left", paddingRight: "0"}}>
                            <span className="search-input__stat-display">{this._getStatsDisplay()}</span>
                        </div>
                        <div className="col-xs-6" style={{textAlign: "right", paddingLeft: "0"}}>
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
