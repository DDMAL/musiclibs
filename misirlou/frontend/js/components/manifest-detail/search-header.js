import React, { PropTypes } from 'react';
import { Link, withRouter } from 'react-router';

import SearchInput from '../search/search-input';

/** Render the navbar with the active page indicated */
export default function SearchHeader({ location, displayUpload })
{
    return (
        <nav className="navbar navbar-default">
            <div className="container-fluid">
                <div className="navbar-header">
                    <Link className="navbar-brand" to="/">Musiclibs</Link>
                </div>
                <div className="nav navbar-nav navbar-left">
                    <SearchInput className="navbar-form" inputClasses="header__search-input"
                                 location={location} />
                </div>
                {displayUpload && (
                    <ul className="nav navbar-nav navbar-right">
                        <NavListItem to="/manifests/upload/">Upload</NavListItem>
                    </ul>
                )}
            </div>
        </nav>
    );
}

/** A thin wrapper around Link which configures the active class */
@withRouter
export class NavListItem extends React.Component
{
    static propTypes = {
        to: PropTypes.string.isRequired,

        children: PropTypes.oneOfType([
            PropTypes.arrayOf(PropTypes.node),
            PropTypes.node
        ]).isRequired,

        router: React.PropTypes.object.isRequired
    };

    render()
    {
        const { to, children, ...conf } = this.props;
        const className = this.props.router.isActive(to) ? 'active' : null;

        return (
            <li className={className}>
                <Link to={to} {...conf}>
                    {children}
                </Link>
            </li>
        );
    }
}