/* eslint-env browser */

// Polyfill the fetch API
import 'whatwg-fetch';

import React from 'react';
import { compose, applyMiddleware, createStore } from 'redux';
import thunk from 'redux-thunk';
import { reduxReactRouter } from 'redux-react-router';
import { createHistory } from 'history';

import rootReducer from './reducers/index';
import Root from './components/root';

const store = compose(
    applyMiddleware(thunk),
    reduxReactRouter({ createHistory })
)(createStore)(rootReducer);

React.render(<Root store={store} />, document.getElementById('content-root'));

export const __hotReload = true;
