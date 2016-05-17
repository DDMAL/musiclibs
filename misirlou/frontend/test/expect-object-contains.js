import expect from 'expect';
import { isEqual } from 'expect/lib/TestUtils';

// FIXME(wabain): How should arrays work?
export default {
    toBeObjectContaining(value)
    {
        expect.assert(
            this.actual && this.actual instanceof Object,
            'Expected %s to be an object', this.actual);

        checkObject(this.actual, value, []);
        return this;
    }
};

function checkObject(actual, value, path)
{
    for (const [key, subValue] of Object.entries(value))
    {
        const actualSubValue = actual[key];

        // We only need an expect assertion if the result might be an error
        if (subValue === actualSubValue)
            continue;

        if (subValue && typeof subValue === 'object' && !Array.isArray(subValue))
        {
            expect.assert(
                actualSubValue instanceof Object,
                'Expected %s to be an object at %s',
                actualSubValue,
                path.concat([key]).join('.')
            );
            checkObject(actualSubValue, subValue, path.concat([key]));
        }
        else
        {
            expect.assert(
                isEqual(actualSubValue, subValue),
                'Expected %s to equal %s at %s',
                actualSubValue,
                subValue,
                path.concat([key]).join('.')
            );
        }
    }
}
