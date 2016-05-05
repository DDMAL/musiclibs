/* eslint-env browser, commonjs */

// Polyfill the fetch API
import 'whatwg-fetch';

import React from 'react';
import ReactDOM from 'react-dom';

import { configureStore } from './redux-store';

const store = configureStore();
const rootElement = document.getElementById('content-root');

let render = () =>
{
    // Request this dynamically so that it can be hot-reloaded
    const Root = require('./components/root').default;
    ReactDOM.render(<Root store={store} />, rootElement);
};

// Support hot reloading of components
// and display an overlay for runtime errors.
// This code is dropped at build time in production.
// Based on https://github.com/reactjs/redux/blob/no-babel-hmre/examples/async/index.js
if (module.hot)
{
    const renderApp = render;

    const renderError = (error) =>
    {
        const RedBox = require('redbox-react');

        ReactDOM.render(
            <RedBox error={error} />,
            rootElement
        );
    };

    render = () =>
    {
        try
        {
            renderApp();
        }
        catch (error)
        {
            console.error(error);
            renderError(error);
        }
    };

    module.hot.accept('./components/root', render);
}

render();
