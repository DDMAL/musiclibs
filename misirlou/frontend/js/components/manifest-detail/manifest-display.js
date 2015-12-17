import React, { PropTypes } from 'react';

import { ERROR } from '../../async-request-status';
import ManifestResource from '../../resources/manifest-resource';

import ErrorAlert from '../ui/error-alert';
import Diva from './diva';

export default class ManifestDisplay extends React.Component {
    static propTypes = {
        manifestRequest: PropTypes.instanceOf(ManifestResource)
    };

    render()
    {
        const req = this.props.manifestRequest;

        if (req && req.status === ERROR)
        {
            return (
                <div className="container">
                    <ErrorAlert error={req.error} />
                </div>
            );
        }

        if (!req || !req.value)
        {
            return (
                <div className="container">
                    <p>Loading...</p>
                </div>
            );
        }

        const config = {
            objectData: req.value.remoteUrl
        };

        return (
            <div className="container-fluid">
                <Diva config={config} />
            </div>
        );
    }
}

export const __hotReload = true;
