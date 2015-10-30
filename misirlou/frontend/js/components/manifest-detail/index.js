import React, { PropTypes } from 'react';
import { createSelector } from 'reselect';
import { connect } from 'react-redux';

import constProp from '../../utils/const-prop';
import * as Manifest from '../../action-creators/manifest';
import AsyncStatusRecord from '../../async-status-record';
import ManifestDisplay from './manifest-display';

const manifestRequestSelector = createSelector(
    state => state.manifests,
    (_, props) => props.params.uuid,
    (manifests, uuid) => ({ manifestRequest: manifests.get(uuid) })
);

@connect(manifestRequestSelector)
export default class ManifestDetailContainer extends React.Component
{
    @constProp
    static get propTypes()
    {
        return {
            params: PropTypes.shape({
                uuid: PropTypes.string.isRequired
            }).isRequired,

            dispatch: PropTypes.func.isRequired,
            manifestRequest: PropTypes.instanceOf(AsyncStatusRecord)
        };
    }

    componentDidMount()
    {
        if (!this.manifestRequest)
            this._loadManifest(this.props.params.uuid);
    }

    componentWillReceiveProps(nextProps)
    {
        if (nextProps.params.uuid !== this.props.params.uuid)
            this._loadManifest(nextProps.params.uuid);
    }

    _loadManifest(uuid)
    {
        this.props.dispatch(Manifest.request({ uuid }));
    }

    render()
    {
        return <ManifestDisplay manifestRequest={this.props.manifestRequest} />;
    }
}

export const __hotReload = true;
