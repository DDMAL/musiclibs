import React, { PropTypes } from 'react';
import { Provider } from 'react-redux';
import { Router, Route, IndexRoute, browserHistory } from 'react-router';

import Landing from './landing/index';
import ManifestUpload from './manifest-upload/index';
import About from './about/index';

export default class Root extends React.Component
{
    static propTypes = {
        store: PropTypes.instanceOf(Object).isRequired
    };

    unlisten = browserHistory.listen(location =>
    {
        window.ga('send', 'pageview', location.pathname);
    });

    componentWillUnmount()
    {
        this.unlisten();
    }

    render()
    {
        return (
            <Provider store={this.props.store}>
                <Router history={browserHistory}>
                    <Route path="/" component={Landing}/>
                    <Route path="/manifests/upload" component={ManifestUpload}/>
                    <Route path="/manifests/:manifestId" component={Landing}/>
                    <Route path="/about" component={About}/>
                </Router>
            </Provider>
        );
    }
}

