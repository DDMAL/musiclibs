
import {GET_STATS } from '../actions';

export default function reduceStats(state = null, action = {})
{
    switch (action.type)
    {
        case GET_STATS:
            return action.response;
        default:
            return state
    }
}
