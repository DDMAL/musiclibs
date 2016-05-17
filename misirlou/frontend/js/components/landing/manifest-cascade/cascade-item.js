import React, { PropTypes } from 'react';
import { Link } from 'react-router';

import './cascade-item.css';
import CascadeItemLabel from './cascade-item-label';
import { manifestSummaryType } from './types';


/** A single manifest in the cascade */
export default class ManifestCascadeItem extends React.Component
{
    static propTypes = {
        manifestSummary: manifestSummaryType.isRequired,

        // Optional
        img: PropTypes.string
    };

    render()
    {
        const { manifestSummary, img } = this.props;

        let imageLayer = null;

        if (img)
        {
            const imageStyle = {
                backgroundImage: `url("${img}")`
            };

            imageLayer = (
                <div className="manifest-cascade__item__background"
                     style={imageStyle} />
            );
        }

        return (
            <Link to={`/manifests/${manifestSummary['local_id']}/`} className="manifest-cascade__item">
                {imageLayer}
                <CascadeItemLabel manifestSummary={manifestSummary} lang="en" />
            </Link>
        );
    }
}

