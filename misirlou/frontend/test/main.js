/* eslint-env commonjs */

import 'babel-polyfill';
import 'whatwg-fetch';

import expect from 'expect';
import expectImmutable from './expect-immutable';
import expectObjectContains from './expect-object-contains';

expect.extend(expectImmutable);
expect.extend(expectObjectContains);

// Load all source files through Webpack to ensure they're counted for code coverage
requireContext(require.context('../js/', true, /\.js$/), (key) =>
{
    // FIXME(wabain): Remove bundle from js/ directory
    return !(key.startsWith('./bundle') || key === './index.js');
});

// Run the test suite
requireContext(require.context('./', true, /.*\.spec\.js$/));

function requireContext(ctx, filter = (k) => k)
{
    ctx.keys().filter(filter).forEach(ctx);
}
