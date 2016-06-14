import React, { PropTypes } from 'react';
import cx from 'classnames';

import * as Search from '../../action-creators/search';
import updateSearch from './search-update-decorator';

@updateSearch
export default class SearchInput extends React.Component
{
    static propTypes = {
        // Optional
        className: PropTypes.string,
        inputClasses: PropTypes.string
    };

    render()
    {
        return (
            <form onSubmit={e => e.preventDefault()} className={this.props.className}>
                <div className="form-group">
                    <input type="search" name="q" placeholder="Search"
                           className={cx('form-control', this.props.inputClasses)}
                           value={this.props.query}
                           onChange={this.props.loadQuery} />
                </div>
            </form>
        );
    }
}
