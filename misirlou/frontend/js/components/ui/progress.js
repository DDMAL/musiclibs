import React from 'react';
import NProgress from 'nprogress';

/**
 * This is a quick and dirty wrapper around the NProgress library.
 * When the component is mounted a spinner appears. This shows loading
 * behavior until the component is unmounted. Note that the progress
 * display is actually global!
 */
export default class Progress extends React.Component {
    componentDidMount()
    {
        NProgress.start();
    }

    componentWillUnmount()
    {
        NProgress.done();
    }

    render()
    {
        return <span />;
    }
}
