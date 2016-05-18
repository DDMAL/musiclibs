'use strict';

var mergeConf = require('./webpack-conf.shared').mergeConf;
var devConf = require('./webpack.config').getDevelopmentConf();

var devServerPort = process.env.npm_package_config_dev_server_port || 8001;
var devServerProxyPort = process.env.npm_package_config_dev_server_proxy_port || 8000;

module.exports = mergeConf(devConf, {
    // We need an absolute URL for the Bootstrap fonts
    // https://github.com/webpack/style-loader/issues/55
    output: {
        publicPath: 'http://localhost:' + devServerPort + devConf.output.publicPath
    },

    devServer: {
        port: devServerPort,

        proxy: {
            '*': 'http://localhost:' + devServerProxyPort
        },

        stats: {
            cached: false
        }
    }
});
