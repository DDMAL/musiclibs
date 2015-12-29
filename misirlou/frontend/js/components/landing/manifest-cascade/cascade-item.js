import React, { PropTypes } from 'react';

import './cascade-item.css!';
import CascadeItemLabel from './cascade-item-label';


const DEFAULT_HEIGHT = 300;


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
        // FIXME
        const { height = DEFAULT_HEIGHT } = this.props;

        const style = {
            height
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
