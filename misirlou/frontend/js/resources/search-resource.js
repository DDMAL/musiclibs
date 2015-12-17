import Im from 'immutable';
import createResourceClass from '../utils/create-resource-class';

export default createResourceClass(
    {
        query: null
    },
    {
        numFound: 0,
        nextPage: null,
        results: Im.List()
    },
    ['query']
);
