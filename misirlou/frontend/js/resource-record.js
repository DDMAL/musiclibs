import Im from 'immutable';
import { ERROR, PROCESSING, SUCCESS } from './async-status-record';

const BaseResource = Im.Record({
    value: null,
    error: null,
    status: null
});

export default class Resource extends BaseResource
{
    resolve()
    {
        if (this.status === ERROR)
            return this.error;

        return this.value;
    }

    setStatus(status, data = null, merger = null)
    {
        switch (status)
        {
            case ERROR:
                return this.merge({
                    status,
                    error: data
                });

            case SUCCESS:
                return this.merge({
                    status,
                    value: merger ? merger(this.value, data) : data,
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
}
