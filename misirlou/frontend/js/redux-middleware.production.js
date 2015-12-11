import thunk from 'redux-thunk';

/** Load redux middleware for production */
export default function getReduxMiddleware()
{
    return [thunk];
}
