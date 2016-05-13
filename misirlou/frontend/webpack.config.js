'use strict';

var webpack = require('webpack');
var ExtractTextPlugin = require('extract-text-webpack-plugin');

var extendBaseConf = require('./webpack-conf.shared');

var pathConf = {
    entry: __dirname + '/js/index.js',

    output: {
        filename: 'main.js',
        path: __dirname + '/js/bundle',
        publicPath: '/static/js/bundle/'
    }
};

var envConf;

if (process.env.NODE_ENV === 'production')
{
    envConf = {
        devtool: 'source-map',

        module: {
            loaders: [
                {
                    test: /\.css$/,
                    loader: ExtractTextPlugin.extract('style-loader', 'css-loader?-url')
                }
            ]
        },

        plugins: [
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
        ]
    };
}
else
{
    envConf = {
        devtool: 'inline-source-map',

        module: {
            loaders: [
                {
                    test: /\.css$/,
                    loader: 'style-loader!css-loader?-url'
                }
            ]
        },

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
}

module.exports = extendBaseConf(pathConf, envConf);
