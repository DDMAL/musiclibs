import React, { PropTypes } from 'react';


export default function ExternalImg({ src })
{
    // TODO(wabain): the maximums probably need to be parameters
    return <img style={{ maxWidth: 200, maxHeight: 200 }} src={src} />;
}

ExternalImg.propTypes = {
    src: PropTypes.string.isRequired
};
