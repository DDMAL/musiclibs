import React from 'react';

import './footer.scss';


export default function Footer()
{
    return (
        <footer>
            <div className="container-fluid">
                <div className="footer--left">
                    <a href="https://github.com/ddmal/musiclibs"><h6>Github</h6></a>
                </div>
                <div className="footer--center">
                    <h6>About us: We are cool</h6>
                </div>
                <div className="footer--right">
                    <a href="https://simssa.ca"><h6>SIMSSA</h6></a>
                </div>
            </div>
        </footer>
    );
}
