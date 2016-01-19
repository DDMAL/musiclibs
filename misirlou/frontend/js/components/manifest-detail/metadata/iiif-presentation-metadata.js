import React, { PropTypes } from 'react';

import DescriptionList from '../../ui/description-list';

import { getLinks, getValues } from './json-ld-accessors';
import { getMetadataTerms, getManifestLinks } from './iiif-manifest-accessors';
import './iiif-presentation-metadata.css!';


/**
 * Render available presentation API metadata
 */
export default function IIIFPresentationMetadata({ manifest, lang })
{
    const id = getLinks(manifest)[0];
    const descriptions = getValues(manifest.description, lang);
    const metadataTerms = getMetadataTerms(manifest.metadata, lang);

    const links = getManifestLinks(manifest);
    const attributions = getValues(manifest.attribution, lang);
    const logos = getLinks(manifest.logo);
    const licenses = getLinks(manifest.license);

    // TODO: services?

    return (
        <div>
            {descriptions.map((description, i) => (
                <p key={i}>{description}</p>
            ))}
            {metadataTerms.length > 0 && <DescriptionList terms={metadataTerms} />}

            <h4>Other links</h4>
            <div><a href={id} target="_blank">Image manifest</a></div>
            {links.map(({ href, text }, i) => (
                <div key={i}><a href={href} target="_blank">{text}</a></div>
            ))}

            <hr />

            <div className="text-center">
                {logos.map((logo, i) => (
                    <img key={i} src={logo} className="iiif-metadata__logo" />
                ))}
                {attributions.map((attribution, i) => (
                    <div key={i}>{attribution}</div>
                ))}
                {licenses.map((license, i) => (
                    <div key={i}>
                        <a href={license} target="_blank">
                            <small className="text-muted">
                                Terms of use {licenses.length > 1 ? `[${i + 1}]` : null}
                            </small>
                        </a>
                    </div>
                ))}
            </div>
        </div>
    );
}

IIIFPresentationMetadata.propTypes = {
    lang: PropTypes.string.isRequired,

    // Don't validate other properties via React
    manifest: PropTypes.shape({
        '@context': PropTypes.oneOfType([PropTypes.string, PropTypes.array]).isRequired,
        '@id': PropTypes.string.isRequired
    }).isRequired
};

export const __hotReload = true;
