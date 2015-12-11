import { compose, applyMiddleware, createStore } from 'redux';
import { reduxReactRouter } from 'redux-react-router';
import { createHistory } from 'history';

import getReduxMiddleware from './redux-middleware';
import rootReducer from './reducers/index';

/** Create a properly configured Redux store */
export function configureStore()
{
    const middleware = getReduxMiddleware();

    return compose(
        applyMiddleware(...middleware),
        reduxReactRouter({ createHistory })
    )(createStore)(rootReducer);
}
