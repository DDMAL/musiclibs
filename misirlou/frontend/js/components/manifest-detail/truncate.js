import React, { PropTypes } from 'react';

const TRUNCATION_REGEX = /^.{0,25}\.+|^\S*/;

export default class Truncate extends React.Component
{
    static propTypes =
    {
        truncation_length: PropTypes.number,
        children: PropTypes.object
    };

    state =
    {
        expanded: false
    }

    _onExpandClick()
    {
        this.setState({expanded: !this.state.expanded})
    }

    render()
    {
        const text = this.props.children.props.children;
        if (text.length < this.props.truncation_length) return <span> {text} </span>
        const expansion_button = this.state.expanded ? '[-]' : '[+]';
        const visible_text =
            this.state.expanded ? text : text.slice(0, this.props.truncation_length) + text.slice(this.props.truncation_length).match(TRUNCATION_REGEX);
        return (
            <span>
                {visible_text} <a style={{cursor: "pointer"}} onClick={() => this._onExpandClick()}>{expansion_button}</a>
            </span>
        );
    }
}
