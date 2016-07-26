import React, { PropTypes } from 'react';

const TRUNCATION_REGEX = /^.{0,25}\.+|^\S*/;

export default class Truncate extends React.Component
{
    static propTypes =
        {
            TruncationLength: PropTypes.number,
            children: PropTypes.object
        };

    state =
        {
            expanded: false
        }

    _onExpandClick()
    {
        this.setState({ expanded: !this.state.expanded });
    }

    render()
    {
        const text = this.props.children.props.children;
        if (text.length < this.props.TruncationLength) return <span> {text} </span>;
        const ExpansionButton = this.state.expanded ? '[-]' : '[+]';
        const VisibleText =
            this.state.expanded ? text : text.slice(0, this.props.TruncationLength) + text.slice(this.props.TruncationLength).match(TRUNCATION_REGEX);
        return (
            <span>
                {VisibleText} <a style={{ cursor: 'pointer' }} onClick={() => this._onExpandClick()}>{ExpansionButton}</a>
            </span>
        );
    }
}
