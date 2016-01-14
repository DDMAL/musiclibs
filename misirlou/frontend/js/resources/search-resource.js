import Im from 'immutable';
import createResourceClass from '../utils/create-resource-class';

export default createResourceClass(
    {
        query: null,
        suggestions: Im.List()
    },
    {
        spellcheck: null,
        numFound: 0,
        nextPage: null,
        results: Im.List()
    },
    ['query']
);
