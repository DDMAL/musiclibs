import React, { PropTypes } from 'react';
import { locationShape } from 'react-router';

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
        search: PropTypes.shape({
            current: PropTypes.instanceOf(SearchResource).isRequired,
            stale: PropTypes.instanceOf(SearchResource).isRequired
        }).isRequired,
        location: locationShape.isRequired
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

    render()
    {
        const pitchBtnText = this.state.pitchSearchShown ? '<< Pitch Search' : '>> Pitch Search';
        return (
            <form onSubmit={e => e.preventDefault()} className={this.props.className}>
                <div className="search-input form-group">
                    <div>
                        <input type="search" name="q" placeholder="Search"
                               className="form-control search-input__input"
                               value={this.props.search.current.query}
                               onChange={this.props.loadQuery} />
                        {this.state.pitchSearchShown && (
                            <input type="search" name="m" placeholder="Pitch Search"
                                   className='form-control search-input__input'
                                   value={this.props.search.current.pitchQuery}
                                   onChange={this.props.loadPitchQuery}/>
                        )}
                    </div>
                    <div className="search-input__pitch-btn--container">
                        <label className="search-input__pitch-btn" onClick={() => this._onPitchBtnClick()}>
                            {pitchBtnText}
                        </label>
                    </div>
                </div>
            </form>
        );
    }
}
