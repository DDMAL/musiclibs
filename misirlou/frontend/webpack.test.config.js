'use strict';

var path = require('path');
var extendBaseConf = require('./webpack-conf.shared');

module.exports = extendBaseConf({
    resolveLoader: {
        root: [path.join(__dirname, 'node_modules'), path.resolve(__dirname, '../../tests/fixtures')]
    },

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
            },

            // Don't load files from js/bundle/
            // FIXME(wabain): The output directory should be moved
            {
                include: path.resolve(__dirname, 'js/bundle'),
                loader: 'null'
            },

            {
                test: /\.js$/,
                include: path.resolve(__dirname, 'js'),
                loader: 'babel-istanbul'
            },

            {
                test: /\.json$/,
                exclude: /node_modules/,
                loader: 'raw'
            }
        ]
    }
});
