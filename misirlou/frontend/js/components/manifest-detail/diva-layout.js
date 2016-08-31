import React, { PropTypes } from 'react';
import { createSelector } from 'reselect';
import { connect } from 'react-redux';
import $ from 'jquery';
import debounce from 'lodash.debounce';

import { SUCCESS, PENDING } from '../../async-request-status';

import * as ManifestActions from '../../action-creators/manifest';
import OMRSearchResultsResource from '../../resources/omr-results-resource';
import Diva from './diva';

/**
 * Wrapper around Diva which handles layout concerns. Initializing
 * Diva with React is awkward because we need access to the DOM to
 * get a reference to the toolbar parent element. This class handles
 * the logic needed to achieve that.
 */

// Debounce interval used for query OMR search results on the page
const DEBOUNCE_INTERVAL = 300;

const getState = createSelector(
    ({ manifests }) => manifests,
    (_, props) => props.manifestId,
    ({ search }) => search,
    (manifests, manifestId, search) => ({
        omrSearchResults: (manifests.get(manifestId) && manifests.get(manifestId).value) ? manifests.get(manifestId).value.omrSearchResults : null,
        results: (search && search.current && search.current.value) ? search.current.value.results : null,
        pitchQuery: (search && search.current) ? search.current.pitchQuery : ''
    })
);

@connect(getState)
export default class DivaLayout extends React.Component
{
    static propTypes = {
        dispatch: PropTypes.func.isRequired,

        // Leave this to be validated by Diva
        config: PropTypes.object.isRequired,

        manifestId: PropTypes.string.isRequired,
        omrSearchResults: PropTypes.instanceOf(OMRSearchResultsResource),
        results: PropTypes.object,
        pitchQuery: PropTypes.string.isRequired,

        // Optional
        toolbarWrapper: PropTypes.func,
        toolbarWrapperProps: PropTypes.object,

        divaWrapper: PropTypes.func,
        divaWrapperProps: PropTypes.object
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

    componentWillReceiveProps(nextProps)
    {
        // How this all works:
        // - New props arrive because the search query has changed
        // - A dispatch is sent to clear the omr search results
        // - New props come in because the manifests have changed
        // - A dispatch is sent to get the highlights on the page
        if (this.props.pitchQuery !== nextProps.pitchQuery
            || this.props.manifestId !== nextProps.manifestId)
        {
            // Clear the highlight regions for the current manuscript
            this.props.dispatch(ManifestActions.clearHighlightLocations(this.props.manifestId));
        }

        // Load the highlights on the page, only when the omr results have been cleared
        const previousOMRResults = this.props.omrSearchResults;
        const nextOMRResults = nextProps.omrSearchResults;

        if (this.props.manifestId === nextProps.manifestId
                && nextOMRResults && nextOMRResults.status === SUCCESS
                && (!previousOMRResults || previousOMRResults !== SUCCESS))
        {
            // Load highlights for the current page
            if (this.refs.diva)
            {
                // FIXME This is a pretty hacky way of getting the diva instance
                const pageIndex = $(this.refs.diva.refs.divaContainer).data('diva').getCurrentPageIndex();
                this._loadPageHighlight(pageIndex, nextProps.pitchQuery);
            }
        }
    }

    _getToolbar()
    {
        const ToolbarWrapper = this.props.toolbarWrapper;
        const additionalProps = this.props.toolbarWrapperProps;

        const toolbar = <div ref="toolbar" />;

        return wrap(toolbar, ToolbarWrapper, additionalProps);
    }

    _getDiva()
    {
        const DivaWrapper = this.props.divaWrapper;
        const additionalProps = this.props.divaWrapperProps;

        const config = {
            ...this.props.config,
            toolbarParentObject: this.state.toolbarParent
        };

        // Get the first OMR result in order to move the diva viewer to the right page
        // Those results are ordered by page number so the first one is the first one to appear
        let firstHighlightPage = null;
        if (this.props.results)
        {
            // Find the result corresponding to the current manifest showed
            for (let i = 0, len = this.props.results.size; i < len; i++)
            {
                if (this.props.results.get(i).local_id === this.props.manifestId && this.props.results.get(i).omr_hits)
                {
                    firstHighlightPage = this.props.results.get(i).omr_hits[0].pagen;
                    break;
                }
            }
        }

        const omrSearchResults = this.props.omrSearchResults;
        const highlights = (omrSearchResults && omrSearchResults.value) ? omrSearchResults.value.highlights : null;

        const diva = (
            <Diva ref="diva" config={config} highlights={highlights} firstHighlightPage={firstHighlightPage}
                           loadPageHighlight={(pageIndex) => this._loadPageHighlight(pageIndex)} />
        );

        return wrap(diva, DivaWrapper, additionalProps);
    }

    _loadPageHighlight = debounce((pageIndex, pitchQuery) =>
    {
        // This method can be called from the diva component which doesn't have access to the pitchQuery
        if (!pitchQuery)
            pitchQuery = this.props.pitchQuery;

        const omrSearchResults = this.props.omrSearchResults;
        const highlights = (omrSearchResults && omrSearchResults.value) ? omrSearchResults.value.highlights : null;
        const status = omrSearchResults ? omrSearchResults.status : null;

        // Only dispatch if the page's highlights aren't already loaded (or pending) and the query is not empty.
        if (status !== PENDING && (!highlights || !highlights.get(pageIndex) && pitchQuery))
        {
            this.props.dispatch(ManifestActions.requestHighlightLocations(this.props.manifestId,
                pageIndex, pitchQuery));
        }
    }, DEBOUNCE_INTERVAL);

    render()
    {
        const toolbar = this._getToolbar();

        // Only initialize Diva once we have access to the toolbar parent element
        const diva = this.state.toolbarParent ? this._getDiva() : null;

        return (
            <div className="propagate-height">
                {toolbar}
                {diva}
            </div>
        );
    }
}


function wrap(element, Wrapper, additionalProps)
{
    if (Wrapper)
        return <Wrapper {...additionalProps}>{element}</Wrapper>;

    return element;
}

