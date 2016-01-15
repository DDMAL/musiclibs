import React, { PropTypes } from 'react';

import ManifestResource from '../../resources/manifest-resource';

import DivaLayout from './diva-layout';

/** Render a Diva viewer and (TODO) display Presentation API metadata */
export default function ManifestViewer({ manifestInfo })
{
    const config = {
        objectData: manifestInfo.remoteUrl
    };

    return (
        <div className="container-fluid">
            <DivaLayout config={config} toolbarWrapper={Row} divaWrapper={Row} />
        </div>
    );
}

ManifestViewer.propTypes = {
    // Optional
    manifestInfo: PropTypes.instanceOf(ManifestResource.ValueClass)
};

/** Wrap children in a full-width column in a Bootstrap row */
function Row({ children }) // eslint-disable-line react/no-multi-comp
{
    return (
        <div className="row">
            <div className="col-md-12">{children}</div>
        </div>
    );
}

export const __hotReload = true;
