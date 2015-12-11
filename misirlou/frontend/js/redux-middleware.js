import Im from 'immutable';
import thunk from 'redux-thunk';
import createReduxLogger from 'redux-logger';

/** Load redux middleware for development */
export default function getReduxMiddleware()
{
    const reduxLogger = createReduxLogger({
        level: 'info',
        transformer: state => Im.Map(state).toJS()
    });

    return [thunk, reduxLogger];
}
