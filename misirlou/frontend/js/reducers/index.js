import { combineReducers } from 'redux';
import { routerStateReducer } from 'redux-react-router';

import manifestsReducer from './manifests-reducer';
import manifestUploadsReducer from './manifest-uploads-reducer';
import searchReducer from './search-reducer';

export default combineReducers({
    router: routerStateReducer,
    manifests: manifestsReducer,
    manifestUploads: manifestUploadsReducer,
    search: searchReducer
});

export const __hotReload = true;
