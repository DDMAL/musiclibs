import expect from 'expect';
import React from 'react';

import shallowRender from '../../shallow-render';
import getFixture from '../../get-fixture';

import ManifestViewer from '../../../js/components/manifest-detail/manifest-viewer';
import DivaLayout from '../../../js/components/manifest-detail/diva-layout';
import IIIFPresentationMetadata from '../../../js/components/manifest-detail/metadata/iiif-presentation-metadata';

describe('components/manifest-detail/manifest-display', () =>
{
    const manifestObject = JSON.parse(getFixture('server:manifest.json'));

    it('should render image and presentation views if manifest is provided', () =>
    {
        const output = shallowRender(<ManifestViewer manifest={manifestObject} />);

        expect(output).toBeObjectContaining({
            type: 'div',
            props: {
                className: 'container-fluid propagate-height',
                children: {
                    type: DivaLayout,

                    // Only check the interesting props here
                    props: {
                        config: {
                            objectData: manifestObject,
                            enableAutoTitle: false,
                            enableImageTitles: false
                        },
                        divaWrapperProps: {
                            metadata: {
                                type: IIIFPresentationMetadata
                            }
                        }
                    }
                }
            }
        });
    });

    it.skip('should render placeholders if no manifest is provided');
});
