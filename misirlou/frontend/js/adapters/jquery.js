'format cjs';

/* eslint-env browser,commonjs */

// FIXME: Get rid of this when it isn't needed!
// See https://github.com/DDMAL/diva.js/issues/292

// We inject the jQuery global into the window because Diva relies on it
// and it can't be easily shimmed with JSPM

const jQuery = require('jquery-vendor');

window.jQuery = jQuery;

module.exports = jQuery;
