import React, { PropTypes } from 'react';
import { connect } from 'react-redux';
import Im from 'immutable';

import ManifestCascadeContainer from './container';

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

    componentWillMount()
    {
        /* eslint-env browser */

        // TODO: Compat
        this._mediaCb = () => this.forceUpdate();
        this._mediaQuery = window.matchMedia(`(min-width: ${MIN_MULTI_COLUMN_WIDTH}px)`);
        this._mediaQuery.addListener(this._mediaCb);
    }

    componentDidMount()
    {
        /* eslint-env browser */

        this._scrollCb = () => this.refs.cascade.considerLoadingMore();
        window.addEventListener('scroll', this._scrollCb);
    }

    componentWillUnmount()
    {
        /* eslint-env browser */

        this._mediaQuery.removeListener(this._mediaCb);
        window.removeEventListener('scroll', this._scrollCb);
    }

    render()
    {
        return (
            <ManifestCascadeContainer ref="cascade"
                    manifests={this.props.manifests}
                    shouldAddToCascade={shouldAddToCascade}
                    onLoadMore={() => this.props.dispatch({ type: 'LOAD_MORE_RECENT_MANIFESTS' })}
                    multiColumn={this._mediaQuery.matches} />
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
    const scrollY = (window.scrollY || window.pageYOffset || document.body.scrollTop + document.documentElement.scrollTop);

    return windowHeight + scrollY === scrollHeight;
}

export const __hotReload = true;
