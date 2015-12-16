import React, { PropTypes } from 'react';
import Im from 'immutable';

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

/** Display a cascade of manifests */
export function ManifestCascade({ columns: columnCount, manifests })
{
    const columnClass = `col-xs-${(12 / columnCount) | 0}`;
    let columnContents;

    if (columnCount === 1)
    {
        columnContents = [manifests.toArray()];
    }
    else
    {
        const heights = Im.Repeat(0, columnCount).toArray();
        columnContents = Im.Repeat(Im.List(), columnCount).toJS();

        for (let [, group] of manifests.groupBy((_, i) => (i / columnCount) | 0))
        {
            // Derive all the assignments of manifests to columns which have different heights
            const layouts = group.reduce((layouts, manifest) => (
                layouts.flatMap(cols => (
                    Im.Range(0, columnCount)
                        .map(i => cols.update(i, col => col.push(manifest)))
                ))
            ), Im.List.of(Im.Repeat(Im.List(), columnCount).toList()));

            // Find the assignment which minimizes the difference between shortest and greatest column height
            const layout = layouts.map(layout =>
            {
                const newHeights = layout.map((col, i) => col.reduce((totalHeight, manifest) => totalHeight + manifest.height, heights[i]));

                return {
                    layout,
                    difference: Math.max(...newHeights) - Math.min(...newHeights)
                };
            }).reduce((best, current) => current.difference < best.difference ? current : best).layout;

            // Push the manifests to their columns
            layout.forEach((newManifests, index) =>
            {
                newManifests.forEach(manifest =>
                {
                    heights[index] += manifest.height;
                    columnContents[index].push(manifest);
                });
            });
        }
    }

    return (
        <div className="row">
            {columnContents.map((manifests, i) => (
                <div key={i} className={columnClass}>
                    {manifests.map((m, j) => <ManifestCascadeItem key={j} manifest={m} />)}
                </div>
            ))}
        </div>
    );
}

ManifestCascade.propTypes = {
    columns: PropTypes.number.isRequired,
    manifests: PropTypes.instanceOf(Im.List).isRequired
};

// TODO
function ManifestCascadeItem({ manifest: { height } })
{
    return <div style={{
        height,
        marginBottom: 30,
        backgroundColor: 'gray',
        backgroundImage: `url(http://placehold.it/200x${height}?text=Manifest!)`,
        backgroundRepeat: 'no-repeat',
        backgroundPosition: 'center'
    }} />;
}

export const __hotReload = true;
