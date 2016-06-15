import React from 'react';

import './footer.scss';


export default function Footer()
{
    return (
        <footer>
            <table>
                <tbody>
                    <tr>
                        <td className="footer--left">
                            <a href="https://twitter.com/simssaproject"><img src="/static/Twitter_logo.png"/></a>
                            <a href="https://github.com/ddmal/musiclibs"><img src="/static/GitHub_logo.png"/></a>
                        </td>
                        <td className="footer--right">
                            <a className="footer__about" href="#"><h5>About</h5></a>
                            <a className="footer__ddmal-logo" href="http://ddmal.music.mcgill.ca/">
                                <img src="/static/DDMAL_logo.png"/>
                            </a>
                            <a href="https://simssa.ca/"><img src="/static/SIMSSA_logo.png"/></a>
                        </td>
                    </tr>
                </tbody>
            </table>
        </footer>
    );
}
