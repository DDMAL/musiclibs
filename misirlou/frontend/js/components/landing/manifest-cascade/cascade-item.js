import React, { PropTypes } from 'react';

import './cascade-item.css!';
import CascadeItemLabel from './cascade-item-label';


// FIXME
export const PLACEHOLDER_MANIFEST_HEIGHT = 250;


/** A single manifest in the cascade */
export default class ManifestCascadeItem extends React.Component
{
    static propTypes = {
        // Optional
        manifest: PropTypes.shape({ /* FIXME */ })
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

        return (
            <div className="manifest-cascade__item" style={style}
                     onMouseEnter={this.showInfo}
                     onMouseLeave={this.hideInfo}
                     onTouchStart={this.showInfo}>
                {this.state.showInfo && <CascadeItemLabel manifest={this.props.manifest} />}
            </div>
        );
    }
}

export const __hotReload = true;
