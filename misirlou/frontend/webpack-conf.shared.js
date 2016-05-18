'use strict';

var webpack = require('webpack');
var mergeWith = require('lodash.mergewith');
var ProgressBarPlugin = require('progress-bar-webpack-plugin');

module.exports = extendBaseConf;
module.exports.mergeConf = mergeConf;

function extendBaseConf()
{
    var sharedJQueryPath = require.resolve('jquery');
    var base = {
        module: {
            loaders: [
                {
                    test: /\.js$/,
                    exclude: /node_modules/,
                    loader: 'babel'
                },
                {
                    // Copy font assets to the bundle directory
                    // https://shellmonger.com/2016/01/22/working-with-fonts-with-webpack/
                    test: /\.(ttf|eot|svg|woff|woff2)$/,
                    loader: 'file?name=fonts/[name].[ext]'
                }
            ]
        },

        resolve: {
            alias: {
                // We need all usages of jQuery to resolve to the same library
                // not only becuase bundling duplicates would be bad (that could
                // be optimized later), but because Diva injects its public code
                // in one of them
                jquery: sharedJQueryPath
            }
        },

        plugins: [
            new ProgressBarPlugin(),

            // Inject globals that Diva relies on. While this plugin applies
            // globally, ESLint should ensure that these aren't injected in
            // app code.
            //
            // Note that we need to get Diva to rely on the shared jQuery instance.
            new webpack.ProvidePlugin({
                'diva': 'diva',
                '$': sharedJQueryPath,
                'jQuery': sharedJQueryPath,
                'window.jQuery': sharedJQueryPath
            })
        ]
    };

    var configs = [base].concat(Array.prototype.slice.call(arguments));

    return configs.reduce(mergeConf);
}

function mergeConf(source, other)
{
    return mergeWith(source, other, mergeFn);
}

// Concatenate arrays together
function mergeFn(source, other)
{
    if (Array.isArray(source))
    {
        return source.concat(other);
    }
}
