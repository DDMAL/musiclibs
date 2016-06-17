import React from 'react';
import { Link } from 'react-router';


import './footer.scss';


export default function Footer()
{
    return (
        <footer>
            <table>
                <tbody>
                    <tr>
                        <td className="footer--left">
                            <a href="https://twitter.com/simssaproject" target="_blank">
                                <img src="/static/Twitter_logo.png"/>
                            </a>
                            <a href="https://github.com/ddmal/musiclibs" target="_blank">
                                <img src="/static/GitHub_logo.png"/>
                            </a>
                        </td>
                        <td className="footer--right">
                            <Link to="/about" className="footer__about" href="#">
                                <h5>About</h5>
                            </Link>
                            <a className="footer__ddmal-logo" href="http://ddmal.music.mcgill.ca/" target="_blank">
                                <img src="/static/DDMAL_logo.png"/>
                            </a>
                            <a href="https://simssa.ca/" target="_blank">
                                <img src="/static/SIMSSA_logo.png"/>
                            </a>
                        </td>
                    </tr>
                </tbody>
            </table>
        </footer>
    );
}
