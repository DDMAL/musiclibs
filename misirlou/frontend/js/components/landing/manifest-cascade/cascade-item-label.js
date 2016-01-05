import React, { PropTypes } from 'react';

import './cascade-item.css!';


/** A single manifest in the cascade */
export default function ManifestCascadeItemLabel({ manifest })
{
    let info;

    // TODO
    if (manifest.remoteManifestLoaded)
        info = <div className="h4">[Manifest things]</div>;
    else if (manifest.error)
        info = <div className="h4 text-center">Error!</div>; // FIXME
    else
        info = <div className="h4 text-center">Loading...</div>;

    return (
        <div className="manifest-cascade__item__label">
            {info}
        </div>
    );
}

ManifestCascadeItemLabel.propTypes = {
    manifest: PropTypes.shape({ /* FIXME */ })
};

export const __hotReload = true;
