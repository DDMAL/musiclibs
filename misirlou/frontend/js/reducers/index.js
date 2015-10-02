import { combineReducers } from 'redux';
import { routerStateReducer } from 'redux-react-router';

import manifestUploadsReducer from './manifest-uploads-reducer';

export default combineReducers({
    router: routerStateReducer,
    manifestUploads: manifestUploadsReducer
});

export const __hotReload = true;
