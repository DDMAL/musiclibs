import React, { PropTypes } from 'react';
import { Link } from 'react-router';

import ManifestResource from '../../../resources/manifest-resource';

import './cascade-item.css!';
import CascadeItemLabel from './cascade-item-label';


/** A single manifest in the cascade */
export default class ManifestCascadeItem extends React.Component
{
    static propTypes = {
        manifest: PropTypes.instanceOf(ManifestResource).isRequired,
        height: PropTypes.number.isRequired,

        // Optional
        img: PropTypes.string
    };

    render()
    {
        const { manifest, height, img } = this.props;

        const style = {
            height
        };

        if (img)
            style.backgroundImage = `url("${img}")`;

        return (
            <Link to={`/manifests/${manifest.id}/`} className="manifest-cascade__item" style={style}>
                <CascadeItemLabel manifest={manifest} lang="en" />
            </Link>
        );
    }
}

export const __hotReload = true;
