import Im from 'immutable';

export const ERROR = 'ERROR';
export const PROCESSING = 'PROCESSING';
export const SUCCESS = 'SUCCESS';

export default Im.Record({
    status: null,
    value: null
});

export const AsyncErrorRecord = Im.Record({ error: null });
