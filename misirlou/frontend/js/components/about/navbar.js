import React, { PropTypes } from 'react';
import { Link, withRouter } from 'react-router';

import '../landing/navbar.scss';

/** Render the navbar with the active page indicated */
export default function Navbar()
{
    return (
        <nav className="navbar navbar-default">
            <div className="container-fluid">
                <div className="navbar-header">
                    <Link className="navbar-brand" to="/">
                        <img height="50" src="/static/musiclibs-logo-lg.png" alt="Musiclibs logo" />
                    </Link>
                </div>
                <div className="nav navbar-nav navbar-left">
                </div>
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
