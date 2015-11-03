import React, { PropTypes } from 'react';
import { createSelector } from 'reselect';
import { connect } from 'react-redux';

import * as Manifest from '../../action-creators/manifest';
import AsyncStatusRecord from '../../async-status-record';
import ManifestDisplay from './manifest-display';

const manifestRequestSelector = createSelector(
    state => state.manifests,
    (_, props) => props.params.manifestId,
    (manifests, id) => ({ manifestRequest: manifests.get(id) })
);

@connect(manifestRequestSelector)
export default class ManifestDetailContainer extends React.Component
{
    static propTypes = {
        params: PropTypes.shape({
            manifestId: PropTypes.string.isRequired
        }).isRequired,

        dispatch: PropTypes.func.isRequired,
        manifestRequest: PropTypes.instanceOf(AsyncStatusRecord)
    };

    componentDidMount()
    {
        if (!this.manifestRequest)
            this._loadManifest(this.props.params.manifestId);
    }

    componentWillReceiveProps(nextProps)
    {
        if (nextProps.params.manifestId !== this.props.params.manifestId)
            this._loadManifest(nextProps.params.manifestId);
    }

    _loadManifest(id)
    {
        this.props.dispatch(Manifest.request({ id }));
    }

    render()
    {
        return <ManifestDisplay manifestRequest={this.props.manifestRequest} />;
    }
}

export const __hotReload = true;
