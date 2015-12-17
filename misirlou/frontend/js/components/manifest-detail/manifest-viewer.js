import React, { PropTypes } from 'react';

import ManifestResource from '../../resources/manifest-resource';

import Diva from './diva';

/** Render a Diva viewer and (TODO) display Presentation API metadata */
export default function ManifestViewer({ manifestInfo })
{
    const config = {
        objectData: manifestInfo.remoteUrl
    };

    return (
        <div className="container-fluid">
            <Diva config={config} />
        </div>
    );
}

ManifestViewer.propTypes = {
    // Optional
    manifestInfo: PropTypes.instanceOf(ManifestResource.ValueClass)
};

export const __hotReload = true;
