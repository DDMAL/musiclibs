import React, { PropTypes } from 'react';

import AsyncStatusRecord, { SUCCESS, ERROR } from '../../async-status-record';

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

                return <Diva config={config} />;

            case ERROR:
                return <div className="alert alert-danger">{`${req.value.error.message}`}</div>;

            default:
                return <p>Loading...</p>;
        }
    }
}

export const __hotReload = true;
