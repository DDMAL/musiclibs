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
    var Spinner = require('cli-spinner').Spinner;
    var spinner = new Spinner('Bundling client code... %s');

    spinner.start();

    createBundleDirectory().then(function ()
    {
        return bundleResources();
    }).then(function ()
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

module.exports = bundleResources;

if (require.main === module)
{
    main();
}
