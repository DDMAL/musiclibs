import React from 'react';
import CSSTransitionGroup from 'react-addons-css-transition-group';
import { locationShape } from 'react-router';

import SearchContainer from '../search/index';
import ManifestCascade from './manifest-cascade/index';

import './landing-page.scss';


const TRANSITION_SETTINGS = {
    transitionName: {
        enter: 'recent-uploads--enter',
        leave: 'recent-uploads--leave'
    },
    transitionEnterTimeout: 400,
    transitionLeaveTimeout: 250
};


/**
 * Render the landing page, which features a search function and a cascade of
 * recently uploaded manifests.
 */
export default function LandingPage({ location })
{
    return (
        <div className="container">
            <h1 className="text-center home-title">Musiclibs</h1>
            <SearchContainer location={location} />
            <CSSTransitionGroup {...TRANSITION_SETTINGS}>
                {!location.query.q && (
                    <section key="recent-section">
                        <header className="page-header">
                            <h2>Recently uploaded</h2>
                        </header>
                        <ManifestCascade />
                    </section>
                )}
            </CSSTransitionGroup>
        </div>
    );
}

LandingPage.propTypes = {
    location: locationShape
};
