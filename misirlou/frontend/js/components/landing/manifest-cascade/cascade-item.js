import React, { PropTypes } from 'react';
import { Link } from 'react-router';
import cx from 'classnames';

import ManifestResource from '../../../resources/manifest-resource';

import './cascade-item.css!';
import CascadeItemLabel from './cascade-item-label';


/** A single manifest in the cascade */
export default class ManifestCascadeItem extends React.Component
{
    static propTypes = {
        manifest: PropTypes.instanceOf(ManifestResource).isRequired,

        // Optional
        img: PropTypes.string
    };

    render()
    {
        const { manifest, img } = this.props;

        const className = cx('manifest-cascade__item', {
            'manifest-cascade__item--loaded': manifest.remoteManifestLoaded,
            'manifest-cascade__item--error': !!manifest.error
        });

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
            <Link to={`/manifests/${manifest.id}/`} className={className}>
                {imageLayer}
                <CascadeItemLabel manifest={manifest} lang="en" />
            </Link>
        );
    }
}

export const __hotReload = true;
