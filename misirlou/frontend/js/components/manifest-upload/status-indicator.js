import React, { PropTypes } from 'react';
import url from 'url';
import { Link } from 'react-router';

import { SUCCESS, ERROR, PENDING } from '../../async-request-status';

import ManifestUploadStatusResource from '../../resources/manifest-upload-status-resource';

import Progress from '../ui/progress';
import ErrorAlert from '../ui/error-alert';

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
            // Unreachable
            return <noscript />;
    }
}

StatusIndicator.propTypes = {
    upload: PropTypes.instanceOf(ManifestUploadStatusResource).isRequired
};

export const __hotReload = true;
