import React, { PropTypes } from 'react';
import $ from 'jquery';
import shallowEquals from 'shallow-equals';
import 'diva.js';
import 'diva.js/build/css/diva.min.css';

import { manifestShape } from './types';


/**
 * Wrapper around a Diva instance, exposing a subset of the Diva lifecycle functions
 */
export default class Diva extends React.Component
{
    static propTypes = {
        config: PropTypes.shape({
            objectData: PropTypes.oneOfType([PropTypes.string, manifestShape]).isRequired
        }).isRequired,

        loadPageHighlight: PropTypes.func.isRequired,

        // Optional
        highlights: PropTypes.array
    };

    constructor()
    {
        super();
        this.state = {
            eventHandler: null
        }
    }

    componentDidMount()
    {
        this._initializeDivaInstance(this.props.config);

        // Register Events
        const handler = window.diva.Events.subscribe('PageDidLoad', this.props.loadPageHighlight);
        this.setState({eventHandler: handler});

        // Only do this when the component is mounted
        if(this.props.highlights)
            this._highlightResults(this.props.highlights);
    }

    /**
     * Destroy and reinitialize the Diva instance whenever the config prop
     * changes. The config equality is tested by shallow comparison of the
     * object values.
     */
    componentWillReceiveProps(nextProps)
    {
        if (!shallowEquals(this.props.config, nextProps.config))
        {
            this._destroyDivaInstance();
            this._initializeDivaInstance(nextProps.config);
        }
    }

    /**
     * We never update the component because the tree from the perspective
     * of React's virtual DOM will never change. Updates to Diva are
     * handled by componentWillReceiveProps().
     * @returns {boolean}
     */
    shouldComponentUpdate()
    {
        return false;
    }

    componentWillUnmount()
    {
        this._destroyDivaInstance();

        // Unsubscribe the events
        const handler = this.state.eventHandler;
        window.diva.Events.unsubscribe(handler);
    }

    _initializeDivaInstance(config)
    {
        // Copy the config because Diva will mutate it
        $(this.refs.divaContainer).diva({ ...config });
    }

    _destroyDivaInstance()
    {
        $(this.refs.divaContainer).data('diva').destroy();
    }

    // TODO Rename hits and refactor to work with what the server will send back
    _highlightResults(hits)
    {
        const divaInstance = $(this.refs.divaContainer).data('diva');

        for (let i = 0, len = hits.length; i < len; i++)
        {
            const pagen = hits[i].pagen - 1;
            let location = [...hits[i].location];
            if (i === 0)
            {
                location[0] = {
                    ...location[0],
                    divID: 'first-highlight-result'
                };
                divaInstance.highlightOnPage(pagen, location);
            }
        }

        // Move to the first result
        divaInstance.gotoHighlight('first-highlight-result');
    }

    render()
    {
        return <div className="propagate-height" ref="divaContainer" />;
    }
}
