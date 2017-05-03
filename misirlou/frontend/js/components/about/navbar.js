import React, { PropTypes } from 'react';
import { Link, withRouter } from 'react-router';

import '../landing/navbar.scss';

/** Render the navbar with the active page indicated */
export default function Navbar()
{
    return (
        <header>
            <div className="header__logo">
                <Link to="/">
                    <img height="50" src="/static/musiclibs-logo-sm.png" alt="Musiclibs logo" className="aboutPageLogo"/>
                </Link>
            </div>
        </header>
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
