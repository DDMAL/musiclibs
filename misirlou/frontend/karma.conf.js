'use strict';

module.exports = function (config)
{
    var webpackConfig = require('./webpack.test.config');

    config.set({
        browsers: ['PhantomJS'],
        files: ['test/main.js'],
        frameworks: ['mocha'],

        preprocessors: {
            'test/main.js': ['webpack', 'sourcemap']
        },

        reporters: ['mocha', 'coverage'],

        coverageReporter: {
            instrumenters: {
                'babel-istanbul': require('babel-istanbul')
            },
            reporters: [
                { type: 'html' },
                { type: 'lcovonly', subdir: '.' },
                { type: 'text-summary' }
            ],
            dir: 'coverage/'
        },

        webpack: webpackConfig,

        webpackMiddleware: {
            noInfo: true
        }
    });
};
