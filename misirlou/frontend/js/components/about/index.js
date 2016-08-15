import React from 'react';

import '../landing/landing-page.scss';
import '../landing/propagate-height.scss';
import Navbar from './navbar';
import Footer from '../landing/footer';

/**
 * Render the about page
 **/
export default function AboutPage()
{
    return (
        <div className="propagate-height propagate-height--root">
            <Navbar />
            <div className="landing--container propagate-height">
            <div className="container">
                <header className="page-header">
                    <h2> About </h2>
                </header>
                    <p>
                        Musiclibs is a new document image search system, created by the <a href="http://ddmal.music.mcgill.ca/">Distributed Digital Music Archives and Libraries lab</a> at the Schulich School of Music, McGill University as part of the <a href="https://simssa.ca/">SIMSSA</a> project.
                        The goal is to present a single interface for searching collections of digitized music documents, using metadata supplied by the original institution, and leading users back to the source of the digitized content for more information.
                    </p>

                    <h3>How it works</h3>
                    <p>
                        Musiclibs is built on the <a href="http://iiif.io/">International Image Interoperability Framework</a> (IIIF).
                        IIIF is an international collaboration of libraries, archives, and documentation centres to provide a standard for image collection interoperability.
                        When an institution makes their image collections available as IIIF <a href="http://iiif.io/api/presentation/2.1/">manifests</a> it provides a way for third-party services, like Musiclibs, to index and display the digitized documents.
                        Metadata from the provider may be embedded in their IIIF manifests, enhancing discoverability by providing additional data for search and discovery.
                        All of the images that are displayed are served directly from the originating organization’s systems.
                        The Musiclibs system does not cache or display images directly.
                    </p>

                    <h3>How to participate</h3>
                    <p>
                        Implementing IIIF in your institution’s digitization architecture is key to participating in the Musiclibs search system.
                        There are two parts to implementing IIIF in your institution: Establishing an image serving system that follows the <a href="http://iiif.io/api/image/2.1/">IIIF Image API</a>, and providing manifests that conform to the <a href="http://iiif.io/api/presentation/2.1/">IIIF presentation API</a>.
                    </p>

                    <h4>IIIF Image API</h4>
                    <p>
                        The IIIF Image API defines a standard URL interface for addressing images in digital collections.
                        It requires a web server or a dedicated image server capable of accepting IIIF-formatted URLs and returning the correct image, or parts of an image, in response.
                    </p>
                    <p>
                        At present, there are a number of image servers that support the IIIF Image API.
                        A list of the servers may be found on the <a href="http://iiif.io/apps-demos/">IIIF site</a> (consult the section on Image Servers).
                    </p>

                    <h4>IIIF Presentation API</h4>
                    <p>
                        The IIIF Presentation API defines a data structure that represents digitized document images; that is, it encodes the sequence of images that form a series of pages, providing a way for document viewers to present a digitized document as a single entity.
                        This data is encoded using JavaScript Object Notation (JSON) and is known as a “manifest.”
                    </p>
                    <p>
                        While the IIIF Presentation API is not a metadata standard, it has minimal provision for exposing metadata about a document, its structure, and contents.
                        It also has a method for a library to provide a link to additional information, in both machine-readable and human-readable forms.

                    </p>

                    <h4>Single Interface for Search</h4>
                    <p>
                        In the Musiclibs search engine, we use the metadata exposed in the IIIF manifests to provide keywords for search and retrieval.
                        The interface for the Musiclibs search engine displays the digitized document when a user clicks on a search result, with clear indications that it is supplied by an external service provider, and that it links back to the source on the host institution’s website.

                    </p>
                    <p>
                        All records shown in the Musiclibs search interface is communicated through the manifest, including descriptive text.
                        For best results, IIIF manifests should contain a <a href="http://iiif.io/api/presentation/2.1/#description">description</a>, label/value pairs in the <a href="http://iiif.io/api/presentation/2.1/#metadata">metadata</a> field, and a link back to the record on the library’s own page using the <a href="http://iiif.io/api/presentation/2.1/#related">related</a> field.
                        Additional fields, such as attribution, license, and institutional logos are also recommended.
                    </p>
                    <p>
                        Libraries may provide links to external machine-readable metadata, such as MARCXML records, using <a href="http://iiif.io/api/presentation/2.1/#seealso">seeAlso</a>.
                        This data may be used to provide further search and retrieval capabilities for these records.
                    </p>

                    <h3>The Future</h3>
                    <p>
                        The Musiclibs search engine is the test-bed for our distributed document image recognition platform, where we will provide “full-music” search (that is, full-text search of music notation) through applying optical music recognition to the sources indexed in Musiclibs.
                        This will provide users with the capability to search music documents by the cataloguing data supplied by libraries, as well as their musical notation contents.
                        For our launch, we are providing two test scores with  which we can demonstrate full-music search, the Salzinnes Antiphonal and the Liber Usualis.
                    </p>

            <hr />
            <div className="row">
                <div className="col-md-6">
                    <a href="http://ddmal.music.mcgill.ca/"><img className="logo" src="/static/DDMAL_logo.png" /></a>
                </div>
                <div className="col-md-6">
                    <a href="https://simssa.ca/"><img className="logo" src="/static/SIMSSA_logo.png" /></a>
                </div>
            </div>
            <div className="row">
                <div className="col-md-6">
                    <br />
                    <a href="http://www.sshrc-crsh.gc.ca/"><img className="logo" src="/static/SSHRC-CRSH_FIP.jpg" /></a>
                </div>
                <div className="col-md-6">
                    <a href="https://www.mcgill.ca/music/music"><img className="logo" src="/static/schulich_logo.png" /></a>
                </div>
            </div>

            </div>
            </div>
            <Footer />
        </div>
    );
}
