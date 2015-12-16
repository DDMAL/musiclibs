import React, { PropTypes } from 'react';
import cx from 'classnames';

export default class SearchInput extends React.Component
{
    static propTypes = {
        onChange: PropTypes.func.isRequired,

        // Optional
        query: PropTypes.string,
        className: PropTypes.string,
        inputClasses: PropTypes.string
    };

    render()
    {
        return (
            <form onSubmit={e => e.preventDefault()} className={this.props.className}>
                <div className="form-group">
                    <input type="search" name="q" placeholder="Search" className={cx('form-control', this.props.inputClasses)} autoFocus={true}
                           value={this.props.query} onChange={this.props.onChange} />
                </div>
            </form>
        );
    }
}

export const __hotReload = true;
