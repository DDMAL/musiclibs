/* eslint-env node */

import { compose, applyMiddleware, createStore } from 'redux';

import rootReducer from './reducers/index';

// Resolved at build time: use different middleware in production
let getReduxMiddleware;

if (process.env.NODE_ENV === 'production')
    getReduxMiddleware = require('./redux-middleware.production').default;
else
    getReduxMiddleware = require('./redux-middleware').default;

/** Create a properly configured Redux store */
export function configureStore()
{
    const middleware = getReduxMiddleware();

    return compose(
        applyMiddleware(...middleware)
    )(createStore)(rootReducer);
}
