import React, { PropTypes } from 'react';

import AsyncStatusRecord, { SUCCESS, ERROR } from '../../async-status-record';

import ErrorAlert from '../ui/error-alert';
import Diva from './diva';

export default class ManifestDisplay extends React.Component {
    static propTypes = {
        manifestRequest: PropTypes.instanceOf(AsyncStatusRecord)
    };

    render()
    {
        const req = this.props.manifestRequest;

        switch (req ? req.status : null)
        {
            case SUCCESS:
                const config = {
                    objectData: req.value.remoteUrl
                };

                return (
                    <div className="container-fluid">
                        <Diva config={config} />
                    </div>
                );

            case ERROR:
                return (
                    <div className="container">
                        <ErrorAlert error={req.value.error} />
                    </div>
                );

            default:
                return (
                    <div className="container">
                        <p>Loading...</p>
                    </div>
                );
        }
    }
}

export const __hotReload = true;
