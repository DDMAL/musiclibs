import React, { PropTypes } from 'react';

import ManifestResource from '../../resources/manifest-resource';

import DivaLayout from './diva-layout';
import IIIFPresentationMetadata from './metadata/iiif-presentation-metadata';
import MetadataPlaceholder from './metadata/placeholder';

/** Render a Diva viewer and display Presentation API metadata */
export default function ManifestViewer({ manifestInfo })
{
    const config = {
        objectData: manifestInfo.remoteUrl,
        enableAutoTitle: false,
        enableImageTitles: false
    };

    let metadata;

    if (manifestInfo.manifest)
        metadata = <IIIFPresentationMetadata manifest={manifestInfo.manifest} lang="en" />;
    else
        metadata = <MetadataPlaceholder />;

    return (
        <div className="container-fluid">
            <DivaLayout config={config}
                        toolbarWrapper={ToolbarWrapper}
                        divaWrapper={DivaWrapper}
                        divaWrapperProps={{ metadata }} />
        </div>
    );
}

ManifestViewer.propTypes = {
    // Optional
    manifestInfo: PropTypes.instanceOf(ManifestResource.ValueClass)
};


/* eslint-disable react/no-multi-comp */

/** Render a Diva viewer and metadata in a two-column row */
function DivaWrapper({ children: diva, metadata })
{
    return (
        <div className="row">
            <div className="col-md-8 col-lg-9">
                {diva}
            </div>
            <div className="col-md-4 col-lg-3">
                {metadata}
            </div>
        </div>
    );
}

DivaWrapper.propTypes = {
    children: PropTypes.element.isRequired,
    metadata: PropTypes.element.isRequired
};


/** Wrap children in a full-width column in a Bootstrap row */
function ToolbarWrapper({ children: toolbar })
{
    return (
        <div className="row">
            <div className="col-md-12">{toolbar}</div>
        </div>
    );
}

ToolbarWrapper.propTypes = {
    children: PropTypes.element.isRequired
};

/* eslint-enable */

export const __hotReload = true;
