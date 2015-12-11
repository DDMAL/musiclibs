/* eslint-env browser */

// Polyfill the fetch API
import 'whatwg-fetch';

import React from 'react';
import ReactDOM from 'react-dom';

import { configureStore } from './redux-store';
import rootReducer from './reducers/index';
import Root from './components/root';

ReactDOM.render(<Root store={configureStore()} />, document.getElementById('content-root'));

export const __hotReload = true;
