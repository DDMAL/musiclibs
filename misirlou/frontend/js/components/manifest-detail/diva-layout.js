import React, { PropTypes } from 'react';
import $ from 'jquery';

import Diva from './diva';

/**
 * Wrapper around Diva which handles layout concerns. Initializing
 * Diva with React is awkward because we need access to the DOM to
 * get a reference to the toolbar parent element. This class handles
 * the logic needed to achieve that.
 */
export default class DivaLayout extends React.Component
{
    static propTypes = {
        config: PropTypes.shape({
            objectData: PropTypes.string.isRequired
        }).isRequired,

        // React will validate on render anyway
        children: PropTypes.any
    };

    constructor()
    {
        super();

        this.state = {
            toolbarParent: null
        };
    }

    componentDidMount()
    {
        // Get a reference to the toolbar as soon as it becomes available
        // this will trigger a rerender, but all that will happen is the
        // rendering of the Diva component
        this.setState({ toolbarParent: $(this.refs.toolbar) }); // eslint-disable-line react/no-did-mount-set-state
    }

    render()
    {
        let diva;
        let divaClass;
        let childColumn;

        // Only initialize once we have access to the toolbar parent
        if (this.state.toolbarParent)
        {
            const config = {
                ...this.props.config,
                toolbarParentObject: this.state.toolbarParent
            };

            diva = <Diva config={config} />;
        }

        if (this.props.children)
        {
            divaClass = 'col-sm-9';
            childColumn = <div className="col-sm-3">{this.props.children}</div>;
        }
        else // eslint-disable-line space-after-keywords
        {
            divaClass = 'col-md-12';
        }

        return (
            <div>
                <div className="row">
                    <div className="col-xs-12" ref="toolbar" />
                </div>
                <div className="row">
                    <div className={divaClass}>{diva}</div>
                    {childColumn}
                </div>
            </div>
        );
    }
}

export const __hotReload = true;
