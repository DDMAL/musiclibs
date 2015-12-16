import React from 'react';

// TODO
/** A single manifest in the cascade */
export default function ManifestCascadeItem({ manifest: { height } })
{
    return (
        <div style={{
            height,
            marginBottom: 30,
            backgroundColor: 'gray',
            backgroundImage: `url(http://placehold.it/200x${height}?text=Manifest!)`,
            backgroundRepeat: 'no-repeat',
            backgroundPosition: 'center'
        }} />
    );
}

export const __hotReload = true;
