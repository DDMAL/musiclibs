import React, { PropTypes } from 'react';

import { manifestShape } from './types';

import DivaLayout from './diva-layout';
import IIIFPresentationMetadata from './metadata/iiif-presentation-metadata';
import MetadataPlaceholder from './metadata/placeholder';

import './propagate-height.scss';


/** Render a Diva viewer and display Presentation API metadata */
export default function ManifestViewer({ manifest })
{
    const config = {
        objectData: manifest, // FIXME: Optional (eventually)
        enableAutoTitle: false,
        enableImageTitles: false
    };

    let metadata;

    if (manifest)
        metadata = <IIIFPresentationMetadata manifest={manifest} lang="en" />;
    else
        metadata = <MetadataPlaceholder />;

    return (
        <div className="container-fluid propagate-height">
            <DivaLayout config={config}
                        toolbarWrapper={ToolbarWrapper}
                        divaWrapper={DivaWrapper}
                        divaWrapperProps={{ metadata }} />
        </div>
    );
}

ManifestViewer.propTypes = {
    // Optional
    manifest: manifestShape
};


/* eslint-disable react/no-multi-comp */

/** Render a Diva viewer and metadata in a two-column row */
function DivaWrapper({ children: diva, metadata })
{
    return (
        <div className="propagate-height propagate-height--row row">
            <div className="propagate-height col-md-8 col-lg-9">
                {diva}
            </div>
            <div className="propagate-height col-md-4 col-lg-3">
                <div className="diva-viewer__metadata propagate-height">
                    {metadata}
                </div>
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
