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

// Funcetion from django docs for easily retrieving csrf token.
export function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
