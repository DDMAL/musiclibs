'use strict';

var jspm = require('jspm');

/** Create a simple bundle of JSPM dependencies */
function bundleResources()
{
    var builder = new jspm.Builder();

    return builder.buildStatic('index.js', 'js/bundle/main.js', {
        sourceMaps: true,
        minify: true
    });
}

module.exports = bundleResources;

if (require.main === module)
{
    var Spinner = require('cli-spinner').Spinner;
    var spinner = new Spinner('Bundling client code... %s');

    spinner.start();

    bundleResources().then(function ()
    {
        spinner.stop();
        process.stdout.write('\n');
        console.log('Bundling complete!');
    },
    function (err)
    {
        spinner.stop();
        process.stdout.write('\n');
        console.error('Bundling failed: %s', err);
    });
}
