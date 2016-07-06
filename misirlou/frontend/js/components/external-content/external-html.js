import React, { PropTypes } from 'react';

import parseHtml from './parse-html';
import ExternalLink from './external-link';
import ExternalImg from './external-img';

const URL_REGEX = RegExp(/https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,4}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)/g);

export default function ExternalHtml({ children: html, ...etc })
{
    html = addLinks(html);
    const doc = parseHtml(html);

    if (!doc)
        return <div />;

    const sanitized = sanitizeHtml(doc.body);

    return <div {...etc}>{sanitized}</div>;
}

ExternalHtml.propTypes = {
    children: PropTypes.string.isRequired
};

export function sanitizeHtml(elem, key)
{
    const nodeName = elem.nodeName.toLowerCase();

    switch (nodeName)
    {
        case '#text':
            return <span key={key}>{elem.nodeValue}</span>;

        case 'a':
            if (!elem.href)
                break;

            return (
                <ExternalLink key={key} href={elem.href}>
                    {sanitizeChildren(elem)}
                </ExternalLink>
            );

        case 'img':
            return <ExternalImg key={key} src={elem.src} />;

        case 'br':
            return <br key={key} />;

        case 'b':
        case 'i':
        case 'p':
            return React.createElement(nodeName, { key }, sanitizeChildren(elem));

        default:
    }

    return (
        <span key={key}>{sanitizeChildren(elem)}</span>
    );
}

export function sanitizeChildren(elem)
{
    const sanitized = [];
    let key = 0;

    for (let node = elem.firstChild; node != null; node = node.nextSibling)
    {
        const sanitizedNode = sanitizeHtml(node, key);

        if (!sanitizedNode)
            continue;

        if (Array.isArray(sanitizedNode))
            sanitized.push(...sanitizedNode);
        else
            sanitized.push(sanitizedNode);

        key++;
    }

    return sanitized;
}

const addLinks = (content) => content.replace(URL_REGEX, '<a href="$&">$&</a>');
