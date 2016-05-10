/** Return a promise which will resolve with the JSON content of the response */
export function getJson(response)
{
    return response.json();
}

/**
 * Return a function that accepts a `fetch` response and throws
 * if the status is not the input status and otherwise returns
 * the response. Useful for promise chaining.
 */
export function expectStatus(status)
{
    return response =>
    {
        if (response.status !== status)
            throw new RequestFailureError(response);

        return response;
    };
}

export class RequestFailureError extends Error {
    constructor(response)
    {
        super(response.statusText);
        this.name = 'RequestFailureError';
        this.response = response;
    }
}

