import React, { PropTypes } from 'react';

import { SUCCESS, ERROR, PENDING } from '../../async-request-status';

import ManifestUploadStatusResource from '../../resources/manifest-upload-status-resource';

import Progress from '../ui/progress';
import ErrorAlert from '../ui/error-alert';

import ImportResult from './import-result';

/**
 * Display a message indicating the status of the upload, or return an
 * empty div if no upload is ongoing
 */
export default function StatusIndicator({ upload })
{
    switch (upload.status)
    {
        case PENDING:
            return <Progress />;

        case ERROR:
            return <ErrorAlert title="Upload failed" error={upload.error} />;

        case SUCCESS:
            return <ImportResult report={upload.value} />;

        default:
            // Unreachable
            return <noscript />;
    }
}

StatusIndicator.propTypes = {
    upload: PropTypes.instanceOf(ManifestUploadStatusResource).isRequired
};

