import React from 'react';

import SearchContainer from '../search/index';
import ManifestCascade from './manifest-cascade/index';

/**
 * Render the landing page, which features a search function and a cascade of
 * recently uploaded manifests.
 */
export default function LandingPage()
{
    return (
        <div className="container">
            <h1 className="text-center">Misirlou</h1>
            <SearchContainer />

            <header className="page-header">
                <h2>Recently uploaded</h2>
            </header>
            <ManifestCascade />
        </div>
    );
}

export const __hotReload = true;
