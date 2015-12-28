import React from 'react';
import { Link, History } from 'react-router';

/** Page layout with navbar */
export default function Page({ children })
{
    return (
        <div>
            <Navbar />
            {children}
        </div>
    );
}

/** Render the navbar with the active page indicated */
export function Navbar()
{
    return (
        <nav className="navbar navbar-default">
            <div className="container">
                <div className="navbar-header">
                    <Link className="navbar-brand" to="/">
                        Misirlou
                    </Link>
                </div>
                <ul className="nav navbar-nav">
                    <NavListItem to="/manifests/upload/">Upload</NavListItem>
                </ul>
            </div>
        </nav>
    );
}

/** A thin wrapper around Link which configures the active class */
export const NavListItem = React.createClass({
    propTypes: {
        to: React.PropTypes.string.isRequired,

        children: React.PropTypes.oneOfType([
            React.PropTypes.arrayOf(React.PropTypes.node),
            React.PropTypes.node
        ]).isRequired
    },

    mixins: [History],

    render()
    {
        const { to, children, ...conf } = this.props;
        const className = this.history.isActive(to) ? 'active' : null;

        return (
            <li className={className}>
                <Link to={to} {...conf}>
                    {children}
                </Link>
            </li>
        );
    }
});

export const __hotReload = true;
