import React, { PropTypes } from 'react';
import constProp from '../utils/const-prop';

export default class SearchInput extends React.Component
{
    @constProp
    static get propTypes()
    {
        return {
            onChange: PropTypes.func.isRequired,

            // Optional
            query: PropTypes.string
        };
    }

    render()
    {
        return (
            <form>
                <div className="form-group">
                    <input type="search" placeholder="Search" className="form-control"
                           value={this.props.query} onChange={this.props.onChange} />
                </div>
            </form>
        );
    }
}

export const __hotReload = true;
