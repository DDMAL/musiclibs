import React, { PropTypes } from 'react';
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
        return <p>UUID is <tt>{this.props.params.uuid}</tt>. More to come...</p>;
    }
}

export const __hotReload = true;
