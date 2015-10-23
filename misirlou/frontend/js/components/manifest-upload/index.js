import React from 'react';
import Im from 'immutable';
import url from 'url';
import { Link } from 'react-router';
import { connect } from 'react-redux';

import constProp from '../../utils/const-prop';
import * as ManifestUpload from '../../action-creators/manifest-upload';

import UploadForm from './upload-form';

@connect(({ manifestUploads }) => ({ manifestUploads }))
export default class ManifestUploadComponent extends React.Component {
    @constProp
    static get propTypes()
    {
        return {
            dispatch: React.PropTypes.func.isRequired,
            manifestUploads: React.PropTypes.instanceOf(Im.Map).isRequired
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
        let submissionDisabled = false;
        let alert = null;

        const upload = this.props.manifestUploads.get(this.state.remoteUrl);

        if (upload)
        {
            // Disable resubmission if the manifest has already been uploaded
            // or if it's being processed
            submissionDisabled = (
                upload.status === ManifestUpload.PROCESSING ||
                upload.status === ManifestUpload.SUCCESS
            );

            switch (upload.status)
            {
                case ManifestUpload.PROCESSING:
                    alert = (
                        <div className="alert">Uploading...</div>
                    );
                    break;

                case ManifestUpload.ERROR:
                    const message = `${upload.value.error.message}`;

                    if (message)
                    {
                        alert = (
                            <div className="alert alert-danger">
                                Upload failed: {message}
                            </div>
                        );
                    }
                    else
                    {
                        alert = <div className="alert alert-danger">Upload failed</div>;
                    }

                    break;

                case ManifestUpload.SUCCESS:
                    // We can't use the fully qualified URL with react-router, so we'll use the absolute path
                    // instead
                    const parsedUrl = url.parse(upload.value.url);
                    let path = parsedUrl.path;

                    if (parsedUrl.hash !== null)
                        path += parsedUrl.hash;

                    alert = (
                        <div className="alert alert-success">
                            Manifest uploaded. <Link className="alert-link" to={path}>View it now.</Link>
                        </div>
                    );
                    break;
            }
        }

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
                {alert}
            </div>
        );
    }
}

export const __hotReload = true;
