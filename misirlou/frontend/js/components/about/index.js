import React, { PropTypes } from 'react';

import '../landing/landing-page.scss';
import '../landing/propagate-height.scss';
import Footer from '../landing/footer';

/**
 * Render the about page
 **/
export default class AboutPage extends React.Component
{
    render()
    {
        return (
            <div className="propagate-height propagate-height--root">
                <div className="landing--container propagate-height">
                <div className="container">
                    <h1> About </h1>
                </div>
                </div>
                <Footer />
            </div>
        );
    }
}
