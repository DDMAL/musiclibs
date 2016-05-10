import React, { PropTypes } from 'react';
import Im from 'immutable';
import { connect } from 'react-redux';

import * as UploadActions from '../../action-creators/manifest-upload';

import UploadPage from './upload-page';

@connect(({ manifestUploads }) => ({ manifestUploads }))
export default class ManifestUploadContainer extends React.Component {
    static propTypes = {
        dispatch: PropTypes.func.isRequired,
        manifestUploads: PropTypes.instanceOf(Im.Map).isRequired
    };

    constructor()
    {
        super();
        this.state = { remoteUrl: '' };
    }

    _handleChange({ target: { value } })
    {
        this.setState({
            remoteUrl: value
        });
    }

    _handleUpload({ remoteUrl })
    {
        this.props.dispatch(UploadActions.upload({ remoteUrl }));
    }

    _handleValidationFailure({ remoteUrl, message })
    {
        this.props.dispatch(UploadActions.validationFailed({
            remoteUrl,
            message
        }));
    }

    render()
    {
        const upload = this.props.manifestUploads.get(this.state.remoteUrl);

        return (
            <UploadPage
                uploadState={upload}
                remoteUrl={this.state.remoteUrl}
                onChange={e => this._handleChange(e)}
                onSubmit={e => this._handleUpload(e)}
                onValidationFailure={e => this._handleValidationFailure(e)} />
        );
    }
}

