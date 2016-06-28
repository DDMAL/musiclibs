import React from 'react';
import { Link } from 'react-router';


import './footer.scss';


export default function Footer()
{
    return (
        <footer>
            <div className="footer-container">
                <div className="footer--left">
                    <a href="https://twitter.com/simssaproject" target="_blank">
                        <img src="/static/Twitter_logo.png"/>
                    </a>
                    <a href="https://github.com/ddmal/musiclibs" target="_blank">
                        <img src="/static/GitHub_logo.png"/>
                    </a>
                </div>
                <div className="footer--right">
                    <Link to="/about" className="footer__about" href="#">
                        <h5>About</h5>
                    </Link>
                    <a href="http://ddmal.music.mcgill.ca/" target="_blank">
                        <img src="/static/DDMAL_logo.png"/>
                    </a>
                    <a className="footer__simssa-logo" href="https://simssa.ca/" target="_blank">
                        <img src="/static/SIMSSA_logo.png"/>
                    </a>
                </div>
            </div>
        </footer>
    );
}
