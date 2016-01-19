import React, { PropTypes } from 'react';

import { getValues } from '../../../utils/json-ld-accessors';

import './cascade-item.css!';

/** A single manifest in the cascade */
export default function ManifestCascadeItemLabel({ manifest: resource, lang })
{
    let info;

    if (resource.remoteManifestLoaded)
    {
        const label = getValues(resource.value.manifest.label, lang).join(' — ') || '[Untitled]';
        const attribution = getValues(resource.value.manifest.attribution, lang);

        info = (
            <div>
                <h3 className="h4">{label}</h3>
                {attribution.map((attrib, i) => (
                    <p key={i}>{attrib}</p>
                ))}
            </div>
        );
    }
    else if (resource.error)
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
    lang: PropTypes.string.isRequired,
    manifest: PropTypes.shape({ /* FIXME */ })
};

export const __hotReload = true;
