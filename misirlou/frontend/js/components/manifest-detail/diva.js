/* global window */

import React, { PropTypes } from 'react';
import $ from 'jquery';
import shallowEquals from 'shallow-equals';
import diva from 'diva.js';
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
        highlights: PropTypes.object,
        firstHighlightPage: PropTypes.number
    };

    constructor(props)
    {
        super(props);

        // Register Events
        const pageLoadHandler = diva.Events.subscribe('PageDidLoad', props.loadPageHighlight);
        const documentLoadHandler = diva.Events.subscribe('DocumentDidLoad', () =>
        {
            // _gotoFirstHighlight is also triggered in componentWillReceiveProps
            // That way, we can be sure that the page will be updated both after the document has loaded
            // (in the case of a search result being clicked) AND in the case the page is refreshed
            // (The Diva document loads before the search results are loaded)
            this.setState({ documentLoaded: true }, () => this._gotoFirstHighlight());
            this._hack_to_display_page();
        });

        this.state = {
            pageLoadHandler,
            documentLoadHandler,
            documentLoaded: false,
            gotoPage: props.firstHighlightPage
        };
    }

    componentDidMount()
    {
        this._initializeDivaInstance(this.props.config);

        // Initial highlighting when first showing a result
        this._gotoFirstHighlight();
    }

    /**
     * Destroy and reinitialize the Diva instance whenever the config prop
     * changes. The config equality is tested by shallow comparison of the
     * object values.
     */
    componentWillReceiveProps(nextProps)
    {
        let manifestIsReady = Boolean(nextProps.config.objectData);
        if (!manifestIsReady)
            return;

        if (!shallowEquals(this.props.config, nextProps.config))
        {
            $(this.refs.divaContainer).data('diva').changeObject(nextProps.config.objectData);
            this.setState({ documentLoaded: false });
        }

        // Only need to change the current page if the firstHighlight page has changed
        if (nextProps.firstHighlightPage && (!this.props.firstHighlightPage ||
            this.props.firstHighlightPage !== nextProps.firstHighlightPage))
        {
            this.setState({ gotoPage: nextProps.firstHighlightPage }, () => this._gotoFirstHighlight());
        }

        if (nextProps.highlights && nextProps.highlights.size)
            this._highlightResults(nextProps.highlights);
        else
            this._clearHighlights();
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
        const pageLoadHandler = this.state.pageLoadHandler;
        const documentLoadHandler = this.state.documentLoadHandler;
        diva.Events.unsubscribe(pageLoadHandler);
        diva.Events.unsubscribe(documentLoadHandler);
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

    _gotoFirstHighlight()
    {
        // Only change page if the Diva document has fully loaded
        // and if there is need to change the current page
        if (this.state.documentLoaded && this.state.gotoPage)
        {
            const divaInstance = $(this.refs.divaContainer).data('diva');
            divaInstance.gotoPageByNumber(this.state.gotoPage);

            this.setState({ gotoPage: null });
        }
    }

    _highlightResults(hits)
    {
        const divaInstance = $(this.refs.divaContainer).data('diva');

        for (const [pageIndex, omrResults] of hits.entries())
        {
            let locations = [];
            for (let i = 0, len = omrResults.length; i < len; i++)
            {
                locations = locations.concat(omrResults[i].location);
            }

            divaInstance.highlightOnPage(pageIndex, locations);
        }
    }

    _clearHighlights()
    {
        const divaInstance = $(this.refs.divaContainer).data('diva');
        divaInstance.resetHighlights();
    }

    _hack_to_display_page()
    {
        const divaInstance = $(this.refs.divaContainer).data('diva');
        const page = divaInstance.getCurrentPageIndex();
        divaInstance.gotoPageByIndex(page+1);
        divaInstance.gotoPageByIndex(page);
    }

    render()
    {
        return <div className="propagate-height" ref="divaContainer" />;
    }
}
