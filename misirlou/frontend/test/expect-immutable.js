import expect from 'expect';
import Im from 'immutable';

export default {
    toBeImmutable(value)
    {
        expect.assert(Im.is(value, this.actual), 'expected %s to be the immutable %s', this.actual, value);
        return this;
    },
    toNotBeImmutable(value)
    {
        expect.assert(!Im.is(value, this.actual), 'expected value not to be the immutable %s', this.actual, value);
        return this;
    }
};
