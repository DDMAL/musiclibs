/**
 * Recursively freeze an object, so that an error will be thrown if it is modified
 * (as long as JS is being executed in strict mode). This is a no-op in production.
 */

let deepFreeze = () =>
{

    /* No-op */
};

// Enforce the immutability of result objects in development
if (Object.freeze && process.env.NODE_ENV !== 'production')
{
    deepFreeze = (obj) =>
    {
        // FIXME: Not doing anything about functions because I'm not worried about
        // them and it's not relevant to this use case
        if (obj && typeof obj === 'object')
        {
            if (!Object.isFrozen(obj))
                Object.freeze(obj);

            for (const prop of Object.getOwnPropertyNames(obj))
                deepFreeze(obj[prop]);
        }
    };
}

export default deepFreeze;
