import React, { PropTypes } from 'react';
import { connect } from 'react-redux';
import Im from 'immutable';

import ManifestCascade from './cascade';

const MIN_MULTI_COLUMN_WIDTH = 500;

// FIXME: get real data

/** Implement all the DOM and Redux glue needed to get the manifest cascade for the landing page */
@connect((s => ({ recentManifests }) => ({ manifests: s }))(Im.List(Im.Range(0, 30).map(() => ({ height: 150 + Math.random() * 200 })))))
export default class LandingPageCascade extends React.Component
{
    static propTypes = {
        manifests: PropTypes.objectOf(Im.List).isRequired,
        dispatch: PropTypes.func.isRequired
    };

    constructor()
    {
        super();

        this._cleanupCallbacks = [];

        this.state = {
            count: 3,
            moreRequested: false
        };
    }

    componentWillMount()
    {
        /* eslint-env browser */

        // TODO: Compat for matchMedia
        this._mediaQuery = window.matchMedia(`(min-width: ${MIN_MULTI_COLUMN_WIDTH}px)`);
    }

    componentDidMount()
    {
        /* eslint-env browser */

        this._setGlobalCallback(
            () => this.forceUpdate(),
            cb => this._mediaQuery.addListener(cb),
            cb => this._mediaQuery.removeListener(cb)
        );

        this._setGlobalCallback(
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
        if (!shouldAddToCascade())
            return;

        const immediatelyAvailable = this.props.manifests.size >= this.state.count + 3;
        let newRequest = false;

        if (!(immediatelyAvailable || this.state.moreRequested))
        {
            newRequest = true;
            this.props.dispatch({ type: 'LOAD_MORE_RECENT_MANIFESTS' });
        }

        const newCount = Math.min(this.state.count + 3, this.props.manifests.size);
        const moreRequested = newRequest || (newCount === this.state.count && this.state.moreRequested);

        const updated = {
            count: newCount,
            moreRequested
        };

        if (Object.keys(updated).some(k => updated[k] !== this.state[k]))
            this.setState(updated);
    }

    /** Fire a listener attachment function and schedule a removal function to be run on unmount */
    _setGlobalCallback(cb, attach, remove)
    {
        attach(cb);
        this._cleanupCallbacks.push(() => remove(cb));
    }

    render()
    {
        return (
            <ManifestCascade manifests={this.props.manifests.slice(0, this.state.count)}
                             columns={this._mediaQuery.matches ? 3 : 1} />
        );
    }
}

/**
 * Add to the manifest cascade when the height of the window is greater than
 * the height of the content or when we've scrolled to the bottom of the screen.
 */
export function shouldAddToCascade()
{
    const windowHeight = document.documentElement.clientHeight;
    const scrollHeight = document.body.scrollHeight;

    if (windowHeight >= scrollHeight)
        return true;

    // http://stackoverflow.com/questions/20514596/document-documentelement-scrolltop-return-value-differs-in-chrome
    // FIXME: this is probably more backwards compatibility than we really need
    const scrollY = (window.scrollY || window.pageYOffset ||
                     document.body.scrollTop + document.documentElement.scrollTop);

    return windowHeight + scrollY === scrollHeight;
}

export const __hotReload = true;
