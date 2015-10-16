import React, { PropTypes } from 'react';
import Diva from './diva';
import constProp from '../../utils/const-prop';

export default class ManifestDetail extends React.Component {
    @constProp
    static get propTypes()
    {
        return {
            params: PropTypes.shape({
                uuid: PropTypes.string.isRequired
            }).isRequired
        };
    }

    render()
    {
        const config = {
            objectData: 'http://www.e-codices.unifr.ch/metadata/iiif/csg-0390/manifest.json'
        };

        return (
            <div>
                <p>UUID is <tt>{this.props.params.uuid}</tt>. More to come...</p>
                <p><strong>Here is an example Diva document:</strong></p>
                <Diva config={config} />
            </div>
        );
    }
}
