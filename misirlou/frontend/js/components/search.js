import React, { PropTypes } from 'react';
import { connect } from 'react-redux';
import SearchInput from './search-input';
import constProp from '../utils/const-prop';

@connect(state => ({ query: state.router.location.query.q }))
export default class Search extends React.Component
{
    @constProp
    static get propTypes()
    {
        return {
            // Optional
            query: PropTypes.string
        };
    }

    render()
    {
        return (
            <div>
                <div className="heading">
                    <h1>Search</h1>
                </div>
                <SearchInput query={this.props.query} />
                <p className="text-muted"><em>Actual results to come</em></p>
            </div>
        );
    }
}
