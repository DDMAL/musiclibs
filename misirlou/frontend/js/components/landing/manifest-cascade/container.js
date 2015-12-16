import React, { PropTypes } from 'react';
import Im from 'immutable';

import ManifestCascade from './cascade';

/** Container component which handles callbacks *** */
export default class ManifestCascadeContainer extends React.Component
{
    static propTypes = {
        manifests: PropTypes.instanceOf(Im.List).isRequired,
        shouldAddToCascade: PropTypes.func.isRequired,
        multiColumn: PropTypes.bool.isRequired,

        // Optional
        onLoadMore: PropTypes.func
    };

    constructor()
    {
        super();

        this.state = {
            count: 3,
            moreRequested: false
        };
    }

    componentDidMount()
    {
        this.considerLoadingMore();
    }

    componentDidUpdate()
    {
        this.considerLoadingMore();
    }

    considerLoadingMore()
    {
        const immediatelyAvailable = this.props.manifests.size >= this.state.count + 3;

        if (!(immediatelyAvailable || this.props.onLoadMore) || !this.props.shouldAddToCascade())
            return;

        let newRequest = false;

        if (!(immediatelyAvailable || this.state.moreRequested))
        {
            newRequest = true;
            this.props.onLoadMore();
        }

        const newCount = Math.min(this.state.count + 3, this.props.manifests.size);
        const moreRequested = newRequest || (newCount === this.state.count && this.state.moreRequested);

        const updated = {
            count: newCount,
            moreRequested
        };

        if (Object.keys(updated).some(k => updated[k] !== this.state[k]))
            this.setState(updated);
    }

    render()
    {
        const { manifests, multiColumn } = this.props;
        return <ManifestCascade manifests={manifests.slice(0, this.state.count)} columns={multiColumn ? 3 : 1} />;
    }
}

export const __hotReload = true;
