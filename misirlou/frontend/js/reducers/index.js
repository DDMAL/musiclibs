import { combineReducers } from 'redux';
import { routerStateReducer } from 'redux-react-router';

export default combineReducers({
    router: routerStateReducer
});

export const __hotReload = true;
