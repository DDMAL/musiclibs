import React, { PropTypes } from 'react';
import { createSelector } from 'reselect';
import { connect } from 'react-redux';
import { locationShape } from 'react-router';

import * as ManifestActions from '../../action-creators/manifest';
import ManifestResource from '../../resources/manifest-resource';
import ManifestDisplay from './manifest-display';
import SearchResults from '../search/search-results';
import SearchHeader from './search-header';

import './manifest-detail.scss';


const manifestRequestSelector = createSelector(
    state => state.manifests,
    (_, props) => props.params.manifestId,
    (manifests, id) => ({ manifestRequest: manifests.get(id) })
);

@connect(manifestRequestSelector)
export default class ManifestDetailContainer extends React.Component {
    static propTypes = {
        params: PropTypes.shape({
            manifestId: PropTypes.string.isRequired
        }).isRequired,

        location: locationShape,
        routes: PropTypes.array.isRequired,

        dispatch: PropTypes.func.isRequired,
        manifestRequest: PropTypes.instanceOf(ManifestResource)
    };

    componentDidMount()
    {
        // Load the manifest if it isn't already loaded
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
        this.props.dispatch(ManifestActions.request({id}));
    }

    render()
    {
        return (
            <div className="propagate-height propagate-height--root">
                <SearchHeader location={this.props.location} displayUpload={true} />
                <div className="manifest-detail propagate-height propagate-height--row">
                    <div className="manifest-detail__search-results">
                        <SearchResults location={this.props.location} />
                    </div>
                    <ManifestDisplay manifestRequest={this.props.manifestRequest} />
                </div>
            </div>
        );
    }
}
