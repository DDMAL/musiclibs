import React, { PropTypes } from 'react';

import { SUCCESS, PENDING } from '../../async-request-status';

import ManifestUploadStatusResource from '../../resources/manifest-upload-status-resource';

import UploadForm from './upload-form';
import StatusIndicator from './status-indicator';

/**
 * Display the manifest upload page, consisting of the header, upload input
 * and the upload status
 */
export default function UploadPage({ uploadState, remoteUrl, ...handlers })
{
    const status = uploadState ? uploadState.status : null;

    return (
        <div className="container">
            <header className="page-header">
                <h1>Upload</h1>
            </header>
            <UploadForm
                    {...handlers}
                    disabled={status === PENDING || status === SUCCESS}
                    uploading={status === PENDING}
                    remoteUrl={remoteUrl} />
            {uploadState ? <StatusIndicator upload={uploadState} /> : null}
        </div>
    );
}

UploadPage.propTypes = {
    remoteUrl: PropTypes.string.isRequired,

    // Optional
    uploadState: PropTypes.instanceOf(ManifestUploadStatusResource)
};

export const __hotReload = true;
