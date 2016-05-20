import React, { PropTypes } from 'react';

import { getValues } from '../../../utils/json-ld-accessors';

import './cascade-item.scss';
import { manifestSummaryType } from '../../../iiif-types';


/** A single manifest in the cascade */
export default function ManifestCascadeItemLabel({ manifestSummary, lang })
{
    // FIXME(wabain): Can these accesses be simplified?
    const label = getValues(manifestSummary.label, lang).join(' — ') || '[Untitled]';
    const attribution = getValues(manifestSummary.attribution, lang).join(', ');

    return (
        <div className="manifest-cascade__item__label">
            <div>
                <h3 className="h4 manifest-cascade__item__label__field">{label}</h3>
                {attribution && (
                    <p className="manifest-cascade__item__label__field">{attribution}</p>
                )}
            </div>
        </div>
    );
}

ManifestCascadeItemLabel.propTypes = {
    lang: PropTypes.string.isRequired,
    manifestSummary: manifestSummaryType.isRequired
};

