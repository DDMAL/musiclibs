import React, { PropTypes } from 'react';
import $ from 'jquery';
import constProp from '../../utils/const-prop';
import 'diva.js/build/css/diva.min.css!';

// FIXME: Get rid of this when it isn't needed!
// See https://github.com/DDMAL/diva.js/issues/292
// Inject the jQuery global into the window because Diva relies on it
// and it can't be easily shimmed with JSPM
window.jQuery = $; // eslint-disable-line

// We need to load Diva dynamically to ensure that jQuery gets imported first
const DIVA_INITIALIZATION_PROMISE = System.import('diva.js');

/**
 * Wrapper around a Diva instance, exposing a subset of the Diva lifecycle functions
 */
export default class Diva extends React.Component
{
    @constProp
    static get propTypes()
    {
        return {
            config: PropTypes.instanceOf(Object).isRequired
        };
    }

    constructor()
    {
        super();

        this._initCount = 0;
        this._divaInitialized = false;
        this._mounted = false;
    }

    componentDidMount()
    {
        this._mounted = true;
        this._initializeDivaInstance(this.props.config);
    }

    /**
     * Destroy and reinitialize the Diva instance whenever the config prop
     * changes. The config equality is tested by referential equality.
     */
    componentWillReceiveProps(nextProps)
    {
        if (this.props.config !== nextProps.config)
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
        this._mounted = false;
    }

    _initializeDivaInstance(config)
    {
        this._initCount++;
        const count = this._initCount;

        // Wait until Diva is initialized if necessary
        DIVA_INITIALIZATION_PROMISE.then(() =>
        {
            if (!this._mounted || this._initCount !== count)
                return;

            $(this.refs.divaContainer).diva(config);
            this._divaInitialized = true;
        });
    }

    _destroyDivaInstance()
    {
        if (this._divaInitialized)
        {
            $(this.refs.divaContainer).data('diva').destroy();
            this._divaInitialized = false;
        }

        this._initCount++;
    }

    render()
    {
        return <div ref="divaContainer" />;
    }
}
