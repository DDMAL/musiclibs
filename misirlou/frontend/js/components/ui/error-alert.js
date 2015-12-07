import React, { PropTypes } from 'react';

/** Display a generic error alert */
export default function ErrorAlert({ title, error })
{
    let message;

    if (error && error.message)
        message = `${error.message}`;

    return (
        <div className="alert alert-danger">
            <h2>
                <span className="glyphicon glyphicon-exclamation-sign" aria-hidden={true} />
                <div className="sr-only">Error:</div>
                {''} {title || 'Something went wrong'}
            </h2>
            {message ? <p>{message}</p> : null}
        </div>
    );
}

ErrorAlert.propTypes = {
    // Optional
    title: PropTypes.string,
    error: PropTypes.instanceOf(Error)
};
