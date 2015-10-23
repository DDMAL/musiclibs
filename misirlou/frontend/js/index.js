/* eslint-env browser */

// Polyfill the fetch API
import 'whatwg-fetch';

import React from 'react';
import ReactDOM from 'react-dom';
import Im from 'immutable';
import process from 'process';
import { compose, applyMiddleware, createStore } from 'redux';
import thunk from 'redux-thunk';
import { reduxReactRouter } from 'redux-react-router';
import createReduxLogger from 'redux-logger';
import { createHistory } from 'history';

import rootReducer from './reducers/index';
import Root from './components/root';

/** Create a properly configured Redux store */
function configureStore()
{
    const middleware = [thunk];

    if (process.env.NODE_ENV !== 'production')
    {
        const reduxLogger = createReduxLogger({
            level: 'info',
            transformer: state => Im.Map(state).toJS()
        });

        middleware.push(reduxLogger);
    }

    return compose(
        applyMiddleware(...middleware),
        reduxReactRouter({ createHistory })
    )(createStore)(rootReducer);
}

ReactDOM.render(<Root store={configureStore()} />, document.getElementById('content-root'));

export const __hotReload = true;
