import React from 'react';

export default class UploadForm extends React.Component {
    static propTypes = {
        remoteUrl: React.PropTypes.string.isRequired,

        // Optional
        uploading: React.PropTypes.bool,
        disabled: React.PropTypes.bool,

        // Event handlers
        onChange: React.PropTypes.func.isRequired,
        onValidationFailure: React.PropTypes.func.isRequired,
        onSubmit: React.PropTypes.func.isRequired
    };

    _handleSubmit(e)
    {
        e.preventDefault();

        const input = this.refs.urlInput;
        const remoteUrl = this.props.remoteUrl;

        if (input.validationMessage)
        {
            this.props.onValidationFailure({
                remoteUrl,
                message: input.validationMessage
            });

            return;
        }
        else if (!this.props.remoteUrl)
        {
            // Sanity check: Make sure there's at least a value in the field
            // Leave more advanced validation to the server
            this.props.onValidationFailure({
                remoteUrl,
                message: 'Please fill out this field'
            });

            return;
        }

        this.props.onSubmit({ remoteUrl });
    }

    render()
    {
        return (
            <form action="/manifests" method="post" onSubmit={e => this._handleSubmit(e)}>
                <div className="form-group">
                    <label htmlFor="url-input">Address</label>
                    <div className="input-group">
                        <input id="url-input" ref="urlInput" type="url"
                               value={this.props.remoteUrl}
                               onChange={this.props.onChange}
                               className="form-control"
                               placeholder="http://" autoFocus required />
                        <div className="input-group-btn">
                            <button className="btn btn-default" type="submit"
                                    disabled={this.props.disabled}>
                                {this.props.uploading ? 'Uploading...' : 'Upload'}
                            </button>
                        </div>
                    </div>
                </div>
            </form>
        );
    }
}

export const __hotReload = true;
