import React, { PropTypes } from 'react';
import url from 'url';
import cx from 'classnames';
import { Link } from 'react-router';

import ManifestUploadStatusResource from '../../resources/manifest-upload-status-resource';

import DescriptionList from '../ui/description-list';

import './import-result.scss';


/**
 * Display a message indicating the status of the upload, or return an
 * empty div if no upload is ongoing
 */
export default function ImportResult({ report })
{
    const successful = report.failed.length === 0;

    const messageClass = cx({
        'text-success': successful,
        'text-danger': !successful
    });

    let leadMessage;

    if (successful)
        leadMessage = `${report.total === 1 ? 'Manifest' : 'All manifests'} imported successfully.`;
    else if (report.succeeded.length > 0)
        leadMessage = `${report.succeeded.length} of ${report.total} manifests imported successfully.`;
    else
        leadMessage = 'Import failed.';

    const descriptions = report.failed
        .map(getErrorDescription)
        .concat(report.succeeded.map(getSuccessDescription));

    return (
        <div>
            <p className={messageClass}>{leadMessage}</p>
            <DescriptionList terms={descriptions} />
        </div>
    );
}

function getErrorDescription({ sourceUrl, errors, warnings })
{
    return {
        term: <p>{sourceUrl}</p>,
        description: (
            <div className="import-problem-description">
                {listing('Errors', errors)}
                {warnings.length > 0 && listing('Warnings', warnings)}
            </div>
        )
    };
}

function getSuccessDescription({ sourceUrl, localUrl, warnings })
{
    return {
        term: <p>{sourceUrl}: <Link to={getRelativeUrl(localUrl)}>View it now.</Link></p>,
        description: (
            <div className="import-problem-description">
                {warnings.length > 0 ? listing('Warnings', warnings) : <p>No warnings.</p>}
            </div>
        )
    };
}

function listing(header, items)
{
    return (
        <div>
            <p><b>{header}</b></p>
            <ul>
                {items.map((item, i) => <li key={i}>{item}</li>)}
            </ul>
        </div>
    );
}

function getRelativeUrl(absoluteUrl)
{
    // FIXME(wabain): Use browser-native URL parsing here
    const parsedUrl = url.parse(absoluteUrl);
    let path = parsedUrl.path;

    if (parsedUrl.hash !== null)
        path += parsedUrl.hash;

    return path;
}

ImportResult.propTypes = {
    report: PropTypes.instanceOf(ManifestUploadStatusResource.ValueClass).isRequired
};

