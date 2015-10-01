/* eslint-env browser */

import React from 'react';
import { compose, createStore } from 'redux';
import { reduxReactRouter } from 'redux-react-router';
import { createHistory } from 'history';

import rootReducer from './reducers/index';
import Root from './components/root';

const store = compose(
    reduxReactRouter({ createHistory })
)(createStore)(rootReducer);

React.render(<Root store={store} />, document.getElementById('content-root'));

export const __hotReload = true;
