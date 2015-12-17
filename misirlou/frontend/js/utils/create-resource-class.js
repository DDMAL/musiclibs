import Im from 'immutable';
import pick from 'lodash.pick';
import { ERROR, PROCESSING, SUCCESS } from '../async-request-status';

/**
 * Create a class representing an immutable resource with a
 * status, an error value, and the parameters, properties and defaults
 * which are passed in.
 *
 * Instances of the class have the following shape:
 *
 *     { status, value, error, ...parameters }
 *
 * Where `parameters` refers to parameters used in requesting the resource
 * and `value` is the resource obtained upon a successful request. The
 * value object contains both the request parameters and additional
 * members defined by the second argument.
 *
 * @param parameters
 * @param valueProperties
 * @returns a resource class
 */
export default function createResourceClass(parameters, valueProperties)
{
    const ValueRecord = Im.Record({
        ...parameters,
        ...valueProperties
    });

    const BaseResource = Im.Record({
        ...parameters,
        status: null,
        value: null,
        error: null
    });

    const paramList = Object.keys(parameters);

    class Resource extends BaseResource
    {

        /**
         * Update the resource with a new status and associated data.
         * Data is interpreted as an error if status is ERROR, as value
         * properties if status is SUCCESS, and is ignored otherwise.
         *
         * An optional merge function can be supplied to reconcile
         * data with the existing values in the case where status is
         * SUCCESS. Otherwise, the existing values are overwritten
         * by the values in data.
         *
         * @param status
         * @param data
         * @param mergeFn
         * @returns {Resource}
         */
        setStatus(status, data = null, mergeFn = null)
        {
            switch (status)
            {
                case ERROR:
                    return this.merge({
                        status,
                        error: data
                    });

                case SUCCESS:
                    let newValue;

                    if (mergeFn)
                        newValue = mergeFn(this.value || this.getInitialValue(), data);
                    else if (this.value)
                        newValue = this.value.merge(data);
                    else
                        newValue = this.getInitialValue(data);

                    return this.merge({
                        status,
                        value: newValue,
                        error: null
                    });

                case PROCESSING:
                    return this.merge({
                        status,
                        error: null
                    });

                default:
                    return this;
            }
        }

        /** Get a value object for the resource with defaults */
        getInitialValue(data)
        {
            const currentParams = pick(this, paramList);
            return ValueRecord({ ...currentParams, ...data }); // eslint-disable-line new-cap
        }
    }

    return Resource;
}
