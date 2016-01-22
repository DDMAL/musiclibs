/* global URL: false */
import React, { PropTypes } from 'react';


// FIXME(wabain): Add parsing fallback
const NO_BUILTIN_PARSER = typeof URL === 'undefined';

const WHITELISTED_PROTOCOLS = [
    'http:',
    'https:',
    'mailto:',
    'ftp:',
    'ftps:'
];


export default function ExternalLink({ href, children })
{
    // TODO(wabain): Better failure-case UI
    if (NO_BUILTIN_PARSER)
        return <a title="External links not supported">{children}</a>;

    let allowed = false;
    let parsed = null;

    if (typeof href === 'string')
    {
        try
        {
            parsed = new URL(href);
        }
        catch (e)
        {
            // Pass
        }
    }

    if (parsed && WHITELISTED_PROTOCOLS.indexOf(parsed.protocol) >= 0)
        allowed = true;

    if (allowed)
        return <a href={href} target="_blank">{children}</a>;

    return <a title={`Invalid link ${href}`}>{children}</a>;
}

ExternalLink.propTypes = {
    href: PropTypes.string.isRequired
};

export const __hotReload = true;
