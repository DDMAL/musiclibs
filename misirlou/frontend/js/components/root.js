import React, { PropTypes } from 'react';
import { Provider } from 'react-redux';
import { Router, Route, IndexRoute, browserHistory } from 'react-router';

import Landing from './landing/index';
import ManifestUpload from './manifest-upload/index';

export default class Root extends React.Component
{
    static propTypes = {
        store: PropTypes.instanceOf(Object).isRequired
    };

    render()
    {
        return (
            <Provider store={this.props.store}>
                <Router history={browserHistory}>
                    <Route path="/" component={Landing}/>
                    <Route path="/manifests/upload" component={ManifestUpload}/>
                    <Route path="/manifests/:manifestId" component={Landing}/>
                </Router>
            </Provider>
        );
    }
}

