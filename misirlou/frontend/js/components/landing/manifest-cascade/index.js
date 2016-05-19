/* eslint-env browser */

import React, { PropTypes } from 'react';
import { connect } from 'react-redux';
import { createSelector } from 'reselect';
import Im from 'immutable';

import * as ManifestActions from '../../../action-creators/manifest';

import ManifestCascade from './cascade';


const ALLOWED_SCROLL_TO_BOTTOM_MARGIN = 100;

// FIXME(wabain): These are related to Bootstrap breakpoints in a principled
// way, probably
const BIG_SCREEN_WIDTH = 992;
const MEDIUM_SCREEN_WIDTH = 600;
const LOAD_INCREMENT = 3;


const getState = createSelector(
    state => state.recentManifests,
    (recent) =>
    {
        return {
            recentManifests: recent.value ? recent.value.list : Im.List(),
            recentManifestsLoaded: !!recent.value && !recent.error
        };
    }
);


/** Implement all the DOM and Redux glue needed to get the manifest cascade for the landing page */
@connect(getState)
export default class LandingPageCascade extends React.Component
{
    static propTypes = {
        recentManifests: PropTypes.objectOf(Im.List).isRequired,
        recentManifestsLoaded: PropTypes.bool.isRequired,
        dispatch: PropTypes.func.isRequired
    };

    constructor()
    {
        super();

        this._cleanupCallbacks = [];

        this.state = {
            displayedManifests: Im.List(),
            moreRequested: false
        };
    }

    componentWillMount()
    {
        if (!this.props.recentManifestsLoaded)
            this.props.dispatch(ManifestActions.requestRecent());

        this._considerLoadingMore();

        // TODO: Compat for matchMedia
        this._mediaQueries = {
            big: window.matchMedia(`(min-width: ${BIG_SCREEN_WIDTH}px)`),
            medium: window.matchMedia(`(min-width: ${MEDIUM_SCREEN_WIDTH}px)`)
        };
    }

    componentDidMount()
    {
        // Re-render when the queries change
        for (const key of Object.keys(this._mediaQueries))
        {
            const query = this._mediaQueries[key];

            this._setGlobalListener(
                () => this.forceUpdate(),
                cb => query.addListener(cb),
                cb => query.removeListener(cb)
            );
        }

        this._setGlobalListener(
            () => this._considerLoadingMore(),
            cb => window.addEventListener('scroll', cb),
            cb => window.removeEventListener('scroll', cb)
        );

        this._considerLoadingMore();
    }

    componentDidUpdate()
    {
        this._considerLoadingMore();
    }

    componentWillUnmount()
    {
        this._cleanupCallbacks.forEach(cb => cb());
    }

    _considerLoadingMore()
    {
        if (!scrollNearBottom())
            return;

        const displayedCount = this.state.displayedManifests.size;
        const availableCount = this.props.recentManifests.size;
        const desiredCount = displayedCount + LOAD_INCREMENT;

        let newMss = null;

        if (availableCount > displayedCount)
            newMss = this.props.recentManifests.slice(0, desiredCount);

        const makeRequest = desiredCount > availableCount && !this.state.moreRequested;

        // FIXME(wabain): Have this do something or remove it
        if (makeRequest)
            this.props.dispatch({ type: 'fakeCommand/loadMoreRecentManifests' });

        if (newMss || makeRequest)
        {
            // The `moreRequested` state is set to true when we make a request
            // and reset to false whenever we add new manifest groups
            this.setState({
                displayedManifests: newMss || this.state.displayedManifests,
                moreRequested: makeRequest
            });
        }
    }

    /** Fire a listener attachment function and schedule a removal function to be run on unmount */
    _setGlobalListener(cb, attach, remove)
    {
        attach(cb);
        this._cleanupCallbacks.push(() => remove(cb));
    }

    /** How many columns to render the manifests in */
    _getColumnCount()
    {
        if (this._mediaQueries.big.matches)
            return 3;

        if (this._mediaQueries.medium.matches)
            return 2;

        return 1;
    }

    render()
    {
        const manifestSummaries = this.state.displayedManifests;

        return (
            <ManifestCascade manifestSummaries={manifestSummaries} columns={this._getColumnCount()} />
        );
    }
}

/**
 * Add to the manifest cascade when the height of the window is greater than
 * the height of the content or when we've scrolled to the bottom of the screen.
 */
export function scrollNearBottom()
{
    const windowHeight = document.documentElement.clientHeight;
    const scrollHeight = document.body.scrollHeight;

    if (windowHeight >= scrollHeight)
        return true;

    // http://stackoverflow.com/questions/20514596/document-documentelement-scrolltop-return-value-differs-in-chrome
    // FIXME: this is probably more backwards compatibility than we really need
    const scrollY = (window.scrollY || window.pageYOffset ||
                     document.body.scrollTop + document.documentElement.scrollTop);

    return Math.abs(windowHeight + scrollY - scrollHeight) <= ALLOWED_SCROLL_TO_BOTTOM_MARGIN;
}

