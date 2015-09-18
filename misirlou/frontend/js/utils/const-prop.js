/**
 * Decorator to precompute the value of a constant, static read-only property.
 *
 * Example usage:
 *
 *     class A
 *     {
 *         @constProp
 *         static get foo()
 *         {
 *             return 1;
 *         }
 *     }
 *
 * Here, `foo` will only be executed once, when the class is created.
 */
export default function constProp(cls, prop, spec)
{
    cls[prop] = spec.get();
    return cls;
}
