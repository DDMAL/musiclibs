import Im from 'immutable';
import createResourceClass from '../utils/create-resource-class';

export default createResourceClass(
    {
        query: null,
        pitchQuery: null,
        suggestions: Im.List()
    },
    {
        spellcheck: null,
        appliedCorrection: null,
        numFound: 0,
        nextPage: null,
        results: Im.List()
    },
    ['query', 'pitchQuery']
);
