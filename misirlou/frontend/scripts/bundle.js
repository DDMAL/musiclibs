'use strict';

var fs = require('fs');
var Promise = require('bluebird');
var jspm = require('jspm');

var stat = Promise.promisify(fs.stat);
var mkdir = Promise.promisify(fs.mkdir);

/** Create a simple bundle of JSPM dependencies */
function bundleResources()
{
    var builder = new jspm.Builder();

    return builder.buildStatic('index.js', 'js/bundle/main.js', {
        sourceMaps: true,
        minify: true
    });
}

/** Create the directory js/bundle if it does not exist */
function createBundleDirectory()
{
    return stat('js/bundle').catch(function ()
    {
        return mkdir('js/bundle');
    });
}

/** Run the bundle function, logging to the console */
function main()
{
    var START_MESSAGE = 'Bundling client code...';

    var spinner;

    var endSpinning = function ()
    {
        if (spinner)
        {
            spinner.stop();
            process.stdout.write('\n');
        }
    };

    if (process.stdout.isTTY)
    {
        var Spinner = require('cli-spinner').Spinner;
        spinner = new Spinner(START_MESSAGE + ' %s');

        spinner.start();
    }
    else
    { // eslint-disable-line space-after-keywords
        console.log(START_MESSAGE);
    }

    createBundleDirectory().then(function ()
    {
        return bundleResources();
    }).then(function ()
    {
        endSpinning();
        console.log('Bundling complete!');
    },
    function (err)
    {
        endSpinning();
        console.error('Bundling failed: %s', err);
        process.exit(1);
    });
}

module.exports = bundleResources;

if (require.main === module)
{
    main();
}
