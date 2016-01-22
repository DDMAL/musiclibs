// Adapted from https://gist.github.com/eligrey/1129031

/* global DOMParser, document */

let parseHtml;
let nativeParsingSupport = false;

// Firefox/Opera/IE throw errors on unsupported types
try
{
    // WebKit returns null on unsupported types
    if ((new DOMParser()).parseFromString('', 'text/html'))
        nativeParsingSupport = true;
}
catch (ex)
{
    // Pass
}

if (nativeParsingSupport)
{
    const parser = new DOMParser();

    parseHtml = function parseHtml(markup)
    {
        return parser.parseFromString(markup, 'text/html');
    };
}
else
{
    parseHtml = function parseHtml(markup)
    {
        const doc = document.implementation.createHTMLDocument('');

        if (markup.toLowerCase().indexOf('<!doctype') > -1)
            doc.documentElement.innerHTML = markup;
        else
            doc.body.innerHTML = markup;

        return doc;
    };
}

export default parseHtml;
