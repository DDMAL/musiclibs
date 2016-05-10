import createResourceClass from '../utils/create-resource-class';

export default createResourceClass(
    {
        id: null,
        remoteManifestLoaded: false
    },
    {
        remoteUrl: null,
        manifest: null
    },
    ['id']
);
