import React, { PropTypes } from 'react';
import { Link } from 'react-router';

import ManifestResource from '../../../resources/manifest-resource';

import './cascade-item.css!';
import CascadeItemLabel from './cascade-item-label';


// FIXME
export const PLACEHOLDER_MANIFEST_HEIGHT = 250;


/** A single manifest in the cascade */
export default class ManifestCascadeItem extends React.Component
{
    static propTypes = {
        manifest: PropTypes.instanceOf(ManifestResource).isRequired
    };

    constructor()
    {
        super();
        this.state = { showInfo: false };
    }

    showInfo = () =>
    {
        this.setState({ showInfo: true });
    };

    hideInfo = () =>
    {
        this.setState({ showInfo: false });
    };

    render()
    {
        const style = {
            height: PLACEHOLDER_MANIFEST_HEIGHT
        };

        const manifest = this.props.manifest;

        return (
            <Link to={`/manifests/${manifest.id}/`} className="manifest-cascade__item" style={style}
                     onMouseEnter={this.showInfo}
                     onMouseLeave={this.hideInfo}
                     onTouchStart={this.showInfo}>
                {this.state.showInfo && <CascadeItemLabel manifest={manifest} lang="en" />}
            </Link>
        );
    }
}

export const __hotReload = true;
