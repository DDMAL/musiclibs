import React from 'react';

import './placeholder.css!';

/** Display a shimmery cribbed-from-Facebook placeholder for IIIF metadata */
export default function MetadataPlaceholder()
{
    // FIXME: Variable copied from Bootstrap. Try to get these programatically?
    const line = 14;
    const lineSkip = 1.42857143 * line - line;
    const padding = 10;

    const { height, masks } = getPlaceholderDimensions([
        // Description
        { percentWidth: 97, height: line + lineSkip },
        { percentWidth: 95, height: line + lineSkip },
        { percentWidth: 96, height: line + lineSkip },
        { percentWidth: 50, height: line + lineSkip, skip: padding },

        // Metadata pairs
        { percentWidth: 5, height: line, skip: lineSkip },
        { percentWidth: 10, height: line, skip: lineSkip },
        { percentWidth: 20, height: line, skip: lineSkip },
        { percentWidth: 60, height: line, skip: lineSkip },
        { percentWidth: 7, height: line, skip: lineSkip },
        { percentWidth: 15, height: line, skip: lineSkip + padding * 2 },

        // Horizontal rule
        { percentWidth: 100, height: 1, skip: padding * 2 - 1 },

        // Attribution
        { percentWidth: 20, height: line, skip: lineSkip, centered: true }
    ]);

    return (
        <div>
            <div className="metadata-placeholder__animation" style={{ height }}>
                {masks.map((dimensions, i) => (
                    <div key={i} className="metadata-placeholder__mask" style={dimensions} />
                ))}
            </div>
        </div>
    );
}

function getPlaceholderDimensions(blocks)
{
    const masks = [];
    let top = 0;

    for (const { percentWidth, height, skip = 0, centered = false } of blocks)
    {
        if (centered)
        {
            const primaryStyle = {
                ...getBoundedWidthFromPercentage((100 - percentWidth) / 2, 225),
                height,
                top
            };

            masks.push(primaryStyle, { ...primaryStyle, right: 0 });
        }
        else
        {
            masks.push({
                ...getBoundedWidthFromPercentage(100 - percentWidth, 225),
                height,
                top,
                right: 0
            });
        }

        if (skip)
        {
            masks.push({
                top: top + height,
                height: skip,
                width: '100%'
            });
        }

        top += height + skip;
    }

    return {
        height: top,
        masks
    };
}

/** Get the width from a percentage *** */
function getBoundedWidthFromPercentage(percentWidth, minContainer)
{
    return {
        width: `${percentWidth}%`,
        minWidth: percentWidth / 100 * minContainer
    };
}

export const __hotReload = true;
