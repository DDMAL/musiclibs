import React, { PropTypes } from 'react';

const TRUNCATION_REGEX = /^.{0,25}\.+|^\S*/;

export default class Truncate extends React.Component
{
    static propTypes =
        {
            truncationLength: PropTypes.number,
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
        if (text.length < this.props.truncationLength) return <span> {text} </span>;
        const ExpansionButton = this.state.expanded ? '[-]' : '[+]';
        const VisibleText =
            this.state.expanded ? text : text.slice(0, this.props.truncationLength) + text.slice(this.props.truncationLength).match(TRUNCATION_REGEX);
        return (
            <span>
                {VisibleText} <a style={{ cursor: 'pointer' }} onClick={() => this._onExpandClick()}>{ExpansionButton}</a>
            </span>
        );
    }
}
