import React, { PropTypes } from 'react';
import constProp from '../utils/const-prop';

export default class SearchInput extends React.Component
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
        // TODO: hook up onChange so that the state is updated when the user types
        return (
            <form>
                <div className="form-group">
                    <input type="search" placeholder="Search" className="form-control"
                           defaultValue={this.props.query} />
                </div>
            </form>
        );
    }
}
