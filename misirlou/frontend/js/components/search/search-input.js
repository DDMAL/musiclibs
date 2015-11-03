import React, { PropTypes } from 'react';

export default class SearchInput extends React.Component
{
    static propTypes = {
        onChange: PropTypes.func.isRequired,

        // Optional
        query: PropTypes.string
    };

    render()
    {
        return (
            <form>
                <div className="form-group">
                    <input type="search" placeholder="Search" className="form-control" autoFocus={true}
                           value={this.props.query} onChange={this.props.onChange} />
                </div>
            </form>
        );
    }
}

export const __hotReload = true;
