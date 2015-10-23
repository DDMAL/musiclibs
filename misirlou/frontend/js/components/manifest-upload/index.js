import React, { PropTypes } from 'react';
import Im from 'immutable';
import url from 'url';
import { Link } from 'react-router';
import { connect } from 'react-redux';

import constProp from '../../utils/const-prop';
import * as ManifestUpload from '../../action-creators/manifest-upload';
import AsyncStatusRecord from '../../async-status-record';

import UploadForm from './upload-form';

@connect(({ manifestUploads }) => ({ manifestUploads }))
export default class ManifestUploadComponent extends React.Component {
    @constProp
    static get propTypes()
    {
        return {
            dispatch: PropTypes.func.isRequired,
            manifestUploads: PropTypes.instanceOf(Im.Map).isRequired
        };
    }

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
        this.props.dispatch(ManifestUpload.upload({ remoteUrl }));
    }

    _handleValidationFailure({ remoteUrl, message })
    {
        this.props.dispatch(ManifestUpload.validationFailed({
            remoteUrl,
            message
        }));
    }

    render()
    {
        const upload = this.props.manifestUploads.get(this.state.remoteUrl);
        const submissionDisabled = upload && (
            upload.status === ManifestUpload.PROCESSING ||
            upload.status === ManifestUpload.SUCCESS
        );

        return (
            <div>
                <header className="page-header">
                    <h1>Upload</h1>
                </header>
                <UploadForm
                    disabled={submissionDisabled}
                    remoteUrl={this.state.remoteUrl}
                    onChange={e => this._handleChange(e)}
                    onSubmit={e => this._handleUpload(e)}
                    onValidationFailure={e => this._handleValidationFailure(e)} />
                <StatusMessage upload={upload} />
            </div>
        );
    }
}

/**
 * Display a message indicating the status of the upload, or return an
 * empty div if no upload is ongoing
 */
export function StatusMessage({ upload })
{
    switch (upload ? upload.status : null)
    {
        case ManifestUpload.PROCESSING:
            return <div className="alert">Uploading...</div>;

        case ManifestUpload.ERROR:
            const message = `${upload.value.error.message}`;

            if (message)
            {
                return (
                    <div className="alert alert-danger">
                        Upload failed: {message}
                    </div>
                );
            }

            return <div className="alert alert-danger">Upload failed</div>;

        case ManifestUpload.SUCCESS:
            // We can't use the fully qualified URL with react-router, so we'll use the absolute path
            // instead
            const parsedUrl = url.parse(upload.value.url);
            let path = parsedUrl.path;

            if (parsedUrl.hash !== null)
                path += parsedUrl.hash;

            return (
                <div className="alert alert-success">
                    Manifest uploaded. <Link className="alert-link" to={path}>View it now.</Link>
                </div>
            );

        default:
            return <div />;
    }
}

StatusMessage.propTypes = {
    // Optional
    upload: PropTypes.objectOf(AsyncStatusRecord)
};

export const __hotReload = true;
