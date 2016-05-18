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

module.exports = (process.env.NODE_ENV === 'production') ? getProductionConf() : getDevelopmentConf();

module.exports.getProductionConf = getProductionConf;
module.exports.getDevelopmentConf = getDevelopmentConf;

function getProductionConf()
{
    return extendBaseConf(pathConf, {
        devtool: 'source-map',

        module: {
            loaders: [
                {
                    test: /\.scss$/,
                    loader: ExtractTextPlugin.extract('style-loader', 'css-loader!sass-loader')
                },

                {
                    test: /\.css$/,
                    loader: ExtractTextPlugin.extract('style-loader', 'css-loader')
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
    });
}

function getDevelopmentConf()
{
    return extendBaseConf(pathConf, {
        devtool: 'inline-source-map',

        module: {
            loaders: [
                {
                    test: /\.scss$/,
                    loader: 'style-loader!css-loader!sass-loader'
                },

                {
                    test: /\.css$/,
                    loader: 'style-loader!css-loader'
                }
            ]
        }
    });
}
