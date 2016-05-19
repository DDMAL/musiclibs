import createResourceClass from '../utils/create-resource-class';

export default createResourceClass(
    {
        remoteUrl: null
    },
    {
        total: null,
        succeeded: null,
        failed: null
    },
    ['remoteUrl']
);
