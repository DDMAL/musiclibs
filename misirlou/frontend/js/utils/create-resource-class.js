import Im from 'immutable';
import { ERROR, PROCESSING, SUCCESS } from '../async-status-record';

/**
 * Create a class representing an immutable resource with a
 * status, an error value, and the properties and defaults
 * which are passed in.
 */
export default function createResourceClass(valueProps)
{
    const BaseResource = Im.Record({
        ...valueProps,
        status: null,
        error: null
    });

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
                    if (mergeFn)
                    {
                        const updated = this.merge({
                            status,
                            error: null
                        });

                        return mergeFn(updated, data);
                    }

                    return this.merge({
                        status,
                        error: null,
                        ...data
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
    }

    return Resource;
}
