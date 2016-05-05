import { combineReducers } from 'redux';

import manifestsReducer from './manifests-reducer';
import manifestUploadsReducer from './manifest-uploads-reducer';
import recentManifestsReducer from './recent-manifests-reducer';
import searchReducer from './search-reducer';

export default combineReducers({
    manifests: manifestsReducer,
    recentManifests: recentManifestsReducer,
    manifestUploads: manifestUploadsReducer,
    search: searchReducer
});
