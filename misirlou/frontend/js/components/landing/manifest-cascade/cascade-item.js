import React from 'react';
import { Link } from 'react-router';

import './cascade-item.scss';
import CascadeItemImage from './cascade-item-image';
import CascadeItemLabel from './cascade-item-label';
import { manifestSummaryType } from '../../../iiif-types';


/** A single manifest in the cascade */
export default class ManifestCascadeItem extends React.Component
{
    static propTypes = {
        manifestSummary: manifestSummaryType.isRequired
    };

    render()
    {
        const { manifestSummary } = this.props;

        return (
            <Link to={`/manifests/${manifestSummary['local_id']}/`} className="manifest-cascade__item">
                <CascadeItemImage thumbnail={manifestSummary.thumbnail} />
                <CascadeItemLabel manifestSummary={manifestSummary} lang="en" />
            </Link>
        );
    }
}

