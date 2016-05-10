import React from 'react';
import { locationShape } from 'react-router';

import SearchContainer from '../search/index';
import ManifestCascade from './manifest-cascade/index';

/**
 * Render the landing page, which features a search function and a cascade of
 * recently uploaded manifests.
 */
export default function LandingPage({ location })
{
    return (
        <div className="container">
            <h1 className="text-center">Misirlou</h1>
            <SearchContainer location={location} />

            <header className="page-header">
                <h2>Recently uploaded</h2>
            </header>
            <ManifestCascade />
        </div>
    );
}

LandingPage.propTypes = {
    location: locationShape
};
