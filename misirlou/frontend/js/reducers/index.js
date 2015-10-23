import { combineReducers } from 'redux';
import { routerStateReducer } from 'redux-react-router';

import manifestsReducer from './manifests-reducer';
import manifestUploadsReducer from './manifest-uploads-reducer';

export default combineReducers({
    router: routerStateReducer,
    manifests: manifestsReducer,
    manifestUploads: manifestUploadsReducer
});

export const __hotReload = true;
