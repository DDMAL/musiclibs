import React, { PropTypes } from 'react';

import DescriptionList from '../../ui/description-list';
import ExternalLink from '../../external-content/external-link';
import ExternalHtml from '../../external-content/external-html';

import { getLinks, getValues } from '../../../utils/json-ld-accessors';
import { getMetadataTerms, getManifestLinks } from '../../../utils/iiif-manifest-accessors';

import './iiif-presentation-metadata.css';


/**
 * Render available presentation API metadata
 */
export default function IIIFPresentationMetadata({ manifest, lang })
{
    const id = getLinks(manifest)[0];
    const labels = getValues(manifest.label, lang);
    const descriptions = getValues(manifest.description, lang);
    const metadataTerms = getMetadataTerms(manifest.metadata, lang).map(pair =>
    {
        return {
            term: pair.label,
            description: <ExternalHtml>{pair.value}</ExternalHtml>
        };
    });

    const links = getManifestLinks(manifest);
    const attributions = getValues(manifest.attribution, lang);
    const logos = getLinks(manifest.logo);
    const licenses = getLinks(manifest.license);

    // TODO: services?

    return (
        <div>
            {labels.map((title, i) => (
                <h2 key={i} className="h3 iiif-metadata__title">{title}</h2>
            ))}

            {descriptions.map((description, i) => (
                <ExternalHtml className="iiif-metadata__description" key={i}>
                    {description}
                </ExternalHtml>
            ))}

            {metadataTerms.length > 0 && <DescriptionList terms={metadataTerms} />}

            <h4>Other links</h4>

            <div><ExternalLink href={id}>Image manifest</ExternalLink></div>

            {links.reduce((out, { hrefs, label }, i) =>
            {
                out.push(...hrefs.map((href, j) => (
                    <div key={`${i}/${j}`}>
                        <ExternalLink href={href}>{label}</ExternalLink>
                    </div>
                )));

                return out;
            }, [])}

            <hr />

            <div className="text-center">
                {logos.map((logo, i) => (
                    <img key={i} src={logo} className="iiif-metadata__logo" />
                ))}
                {attributions.map((attribution, i) => (
                    <ExternalHtml key={i}>{attribution}</ExternalHtml>
                ))}
                {licenses.map((license, i) => (
                    <div key={i}>
                        <ExternalLink href={license}>
                            <small className="text-muted">
                                Terms of use {licenses.length > 1 ? `[${i + 1}]` : null}
                            </small>
                        </ExternalLink>
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
