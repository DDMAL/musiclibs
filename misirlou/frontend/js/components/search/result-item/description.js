import React, { PropTypes } from 'react';

// Length at which to try to truncate
const TRUNCATION_LENGTH = 150;

// Match up to twenty-five characters followed by periods, or up to the first whitespace character
const TRUNCATION_REGEX = /^.{0,25}\.+|^\S*/;

/** Display the beginning of the description, allowing it to expand if it is longer */
export default class Description extends React.Component
{
    static propTypes = {
        text: PropTypes.string.isRequired
    };

    constructor()
    {
        super();

        this.state = {
            expanded: false
        };
    }

    _handleExpander = evt =>
    {
        evt.preventDefault();

        this.setState({
            expanded: !this.state.expanded
        });
    };

    render()
    {
        let text = this.props.text;
        let expansionTarget;

        if (this.state.expanded)
        {
            expansionTarget = '[-]';
        }
        else if (this.props.text.length > TRUNCATION_LENGTH)
        {
            text = text.slice(0, TRUNCATION_LENGTH) + TRUNCATION_REGEX.exec(text.slice(TRUNCATION_LENGTH))[0];

            if (text !== this.props.text)
                expansionTarget = '[+]';
        }

        return <p>{text} {expansionTarget && <a href="" onClick={this._handleExpander}>{expansionTarget}</a>}</p>;
    }
}

