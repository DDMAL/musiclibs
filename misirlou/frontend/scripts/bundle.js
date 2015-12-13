'use strict';

var fs = require('fs');
var path = require('path');
var Promise = require('bluebird');
var System = require('systemjs');
var jspm = require('jspm');

var stat = Promise.promisify(fs.stat);
var mkdir = Promise.promisify(fs.mkdir);

/** Create a simple bundle of JSPM dependencies */
function bundleResources()
{
    var builder = new jspm.Builder({ normalize: normalizeProduction });

    return builder.buildStatic('index.js', 'js/bundle/main.js', {
        sourceMaps: true,
        minify: true
    });
}

/**
 * Chain on the normalization method to replace development modules with the
 * production versions.
 *
 * Approach inspired by https://github.com/jspm/jspm-cli/issues/621 but
 * I'm not sure this is really the best way.
 */
function normalizeProduction()
{
    // FIXME: Testing the file path is kind of expensive. This should be
    // cached, and files in js/packages shouldn't be tested

    return System.normalize.apply(this, arguments).then(function (result)
    {
        var resultPath = getAbsolutePathFromFileURL(result);

        if (resultPath === null)
            return result;

        var basename = path.basename(resultPath);
        var productionized = basename.replace(/^(.*)(\.[^.]+)$/, '$1.production$2');

        // Bail if deriving the production name failed
        if (productionized === basename)
            return result;

        var productionPath = path.join(path.dirname(resultPath), productionized);

        // Test the path and return resolve with the productionized version if it
        // exists
        return stat(productionPath).then(
            function ()
            {
                return productionPath;
            },
            function ()
            {
                return result;
            }
        );
    });
}

/**
 * Return the absolute path corresponding to a file: protocol URL, or null if
 * the input URL is not a file: URL.
 */
function getAbsolutePathFromFileURL(url)
{
    var pathUri = (/^file:\/\/(\/.*)/).exec(url);

    if (!pathUri)
        return null;

    return pathUri[1];
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
    else // eslint-disable-line space-after-keywords
    {
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
