import { combineReducers } from 'redux';
import { routerStateReducer } from 'redux-react-router';

import manifestsReducer from './manifests-reducer';
import manifestUploadsReducer from './manifest-uploads-reducer';
import recentManifestsReducer from './recent-manifests-reducer';
import searchReducer from './search-reducer';

export default combineReducers({
    router: routerStateReducer,
    manifests: manifestsReducer,
    recentManifests: recentManifestsReducer,
    manifestUploads: manifestUploadsReducer,
    search: searchReducer
});

