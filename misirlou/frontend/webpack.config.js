'use strict';

/* eslint-env node */

var webpack = require('webpack');
var ExtractTextPlugin = require('extract-text-webpack-plugin');
var ProgressBarPlugin = require('progress-bar-webpack-plugin');

var sharedJQueryPath = require.resolve('jquery');

module.exports = {
    entry: __dirname + '/js/index.js',

    output: {
        filename: 'main.js',
        path: __dirname + '/js/bundle',
        publicPath: '/static/js/bundle/'
    },

    module: {
        loaders: [
            {
                test: /\.css$/,
                loader: getCssLoader('style-loader', 'css-loader?-url')
            },
            {
                test: /\.js$/,
                exclude: /node_modules/,
                loader: 'babel'
            }
        ]
    },

    devtool: (process.env.NODE_ENV === 'production') ? 'source-map' : 'inline-source-map',

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
    ].concat(process.env.NODE_ENV === 'production' ? getProductionPlugins() : []),

    devServer: {
        port: process.env.npm_package_config_dev_server_port || 8001,

        proxy: {
            '*': 'http://localhost:' + (process.env.npm_package_config_dev_server_proxy_port || 8000)
        },

        stats: {
            cached: false
        }
    }
};


function getCssLoader(before, loader)
{
    if (process.env.NODE_ENV === 'production')
        return ExtractTextPlugin.extract(before, loader);

    return before + '!' + loader;
}

function getProductionPlugins()
{
    return [
        new ExtractTextPlugin('[name].css'),
        new webpack.DefinePlugin({
            'process.env.NODE_ENV': JSON.stringify('production')
        }),
        new webpack.optimize.UglifyJsPlugin({
            compress: {
                warnings: false
            }
        }),
        new webpack.optimize.OccurrenceOrderPlugin(true)
    ];
}
