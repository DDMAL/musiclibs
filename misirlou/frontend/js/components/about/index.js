import React, { PropTypes } from 'react';

import '../landing/landing-page.scss';
import '../landing/propagate-height.scss';
import Navbar from './navbar';
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
                <Navbar />
                <div className="landing--container propagate-height">
                <div className="container">
                    <header className="page-header">
                        <h2> About </h2>
                    </header>
                </div>
                </div>
                <Footer />
            </div>
        );
    }
}
