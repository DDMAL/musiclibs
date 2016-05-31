import React from 'react';
import { Link, withRouter } from 'react-router';

/** Page layout with navbar */
export default function Page({ children, routes })
{
    // Go through all routes to see if any has the pageClassName attribute
    var pageClassName = '';
    for (var i = 0; i < routes.length; i++)
    {
        if (routes[i].pageClassName)
        {
            pageClassName = routes[i].pageClassName;
            break;
        }
    }

    return (
        <div className={ pageClassName }>
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
                    <Link className="navbar-brand" to="/">Musiclibs</Link>
                </div>
                <ul className="nav navbar-nav">
                    <NavListItem to="/manifests/upload/">Upload</NavListItem>
                </ul>
            </div>
        </nav>
    );
}

/** A thin wrapper around Link which configures the active class */
export const NavListItem = withRouter(React.createClass({
    propTypes: {
        to: React.PropTypes.string.isRequired,

        children: React.PropTypes.oneOfType([
            React.PropTypes.arrayOf(React.PropTypes.node),
            React.PropTypes.node
        ]).isRequired,

        router: React.PropTypes.object.isRequired
    },

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
}));

