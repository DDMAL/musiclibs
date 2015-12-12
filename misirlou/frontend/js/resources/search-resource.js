import Im from 'immutable';
import createResourceClass from '../utils/create-resource-class';

export default createResourceClass({
    query: null,
    numFound: null,
    nextPage: null,
    results: Im.List()
});
