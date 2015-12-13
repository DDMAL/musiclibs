import React, { PropTypes } from 'react';

/** Display a generic error alert */
export default function ErrorAlert({ title, error, children })
{
    return (
        <div className="alert alert-danger">
            <div>
                <span className="glyphicon glyphicon-exclamation-sign" aria-hidden={true} />
                <span className="sr-only">Error:</span>
                {' '}
                <strong>{title || 'Something went wrong'}</strong>
            </div>
            {error && error.message ? <p>{`${error.message}`}</p> : null}
            {children}
        </div>
    );
}

ErrorAlert.propTypes = {
    // Optional
    title: PropTypes.string,
    error: PropTypes.instanceOf(Error)
};
