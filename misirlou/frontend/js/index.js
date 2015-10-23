/* eslint-env browser */

// Polyfill the fetch API
import 'whatwg-fetch';

import React from 'react';
import ReactDOM from 'react-dom';
import Im from 'immutable';
import { compose, applyMiddleware, createStore } from 'redux';
import thunk from 'redux-thunk';
import { reduxReactRouter } from 'redux-react-router';
import createReduxLogger from 'redux-logger';
import { createHistory } from 'history';

import rootReducer from './reducers/index';
import Root from './components/root';

const reduxLogger = createReduxLogger({
    level: 'info',
    transformer: state => Im.Map(state).toJS()
});

const store = compose(
    applyMiddleware(thunk, reduxLogger),
    reduxReactRouter({ createHistory })
)(createStore)(rootReducer);

ReactDOM.render(<Root store={store} />, document.getElementById('content-root'));

export const __hotReload = true;
