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
        // Leave this to be validated by Diva
        config: PropTypes.object.isRequired,

        // Optional
        toolbarWrapper: PropTypes.func,
        divaWrapper: PropTypes.func
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

    _getToolbar()
    {
        const ToolbarWrapper = this.props.toolbarWrapper;
        const toolbar = <div ref="toolbar" />;

        if (ToolbarWrapper)
            return <ToolbarWrapper>{toolbar}</ToolbarWrapper>;

        return toolbar;
    }

    _getDiva()
    {
        const DivaWrapper = this.props.divaWrapper;

        const config = {
            ...this.props.config,
            toolbarParentObject: this.state.toolbarParent
        };

        const diva = <Diva config={config} />;

        if (DivaWrapper)
            return <DivaWrapper>{diva}</DivaWrapper>;

        return diva;
    }

    render()
    {
        const toolbar = this._getToolbar();

        // Only initialize Diva once we have access to the toolbar parent element
        const diva = this.state.toolbarParent ? this._getDiva() : null;

        return (
            <div>
                {toolbar}
                {diva}
            </div>
        );
    }
}

export const __hotReload = true;
