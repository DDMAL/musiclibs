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

    render()
    {
        const style = {
            height: PLACEHOLDER_MANIFEST_HEIGHT
        };

        const showInfo = () => this.setState({ showInfo: true });
        const hideInfo = () => this.setState({ showInfo: false });

        return (
            <div className="manifest-cascade__item" style={style} onMouseEnter={showInfo} onMouseLeave={hideInfo} onTouchStart={showInfo}>
                {this.state.showInfo && <CascadeItemLabel manifest={this.props.manifest} />}
            </div>
        );
    }
}

export const __hotReload = true;
