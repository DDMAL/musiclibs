import React, { PropTypes } from 'react';
import { connect } from 'react-redux';
import SearchInput from './search-input';
import constProp from '../utils/const-prop';
import { replaceState } from 'redux-react-router';

@connect(state => ({
    query: state.router.location.query.q,
    pathname: state.router.location.pathname
}))
export default class Search extends React.Component
{
    @constProp
    static get propTypes()
    {
        return {
            dispatch: PropTypes.func.isRequired,
            pathname: PropTypes.string.isRequired,

            // Optional
            query: PropTypes.string
        };
    }

    _handleInput(event)
    {
        const query = event.target.value ? { q: event.target.value } : null;
        this.props.dispatch(replaceState(null, this.props.pathname, query));
    }

    render()
    {
        return (
            <div>
                <header className="page-header">
                    <h1>Search</h1>
                </header>
                <SearchInput query={this.props.query} onChange={this._handleInput.bind(this)} />
                <p className="text-muted"><em>Actual results to come</em></p>
            </div>
        );
    }
}

export const __hotReload = true;
