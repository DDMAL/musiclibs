import React, { PropTypes } from 'react';

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
        console.log("click!");
        this.setState({expanded: !this.state.expanded})
    }

    render()
    {
        const text = this.props.children.props.children;
        const expansion_button = this.state.expanded ? '[-]' : '[+]';
        const visible_text =
            this.state.expanded ? text : text.slice(0, this.props.truncation_length);
        return (
            <span>
                {visible_text} <a style={{cursor: "pointer"}} onClick={() => this._onExpandClick()}>{expansion_button}</a>
            </span>
        );
    }
}
