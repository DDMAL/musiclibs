import expect from 'expect';
import React from 'react';

import shallowRender from '../../shallow-render';
import getFixture from '../../get-fixture';

import { PENDING, SUCCESS, ERROR } from '../../../js/async-request-status';
import ManifestResource from '../../../js/resources/manifest-resource';
import ManifestDisplay from '../../../js/components/manifest-detail/manifest-display';
import ManifestViewer from '../../../js/components/manifest-detail/manifest-viewer';
import ErrorAlert from '../../../js/components/ui/error-alert';

describe('components/manifest-detail/manifest-display', () =>
{
    const uuid = '123e4567-e89b-12d3-a456-426655440000';
    const manifestObject = JSON.parse(getFixture('server:manifest.json'));

    it('should render a loading message if resource status is PENDING', () =>
    {
        const resource = new ManifestResource({
            id: uuid,
            status: PENDING
        });

        const output = shallowRender(<ManifestDisplay manifestRequest={resource} />);

        expect(output).toBeObjectContaining({
            type: 'div',
            props: {
                className: 'container',
                children: {
                    type: 'p',
                    props: {
                        children: 'Loading...'
                    }
                }
            }
        });
    });

    it('should render an error alert in a container if resource status is ERROR', () =>
    {
        const error = new Error('This manifest was broken or something');
        const resource = new ManifestResource({
            id: uuid,
            status: ERROR,
            error
        });

        const output = shallowRender(<ManifestDisplay manifestRequest={resource} />);

        expect(output).toBeObjectContaining({
            type: 'div',
            props: {
                className: 'container',
                children: {
                    type: ErrorAlert,
                    props: {
                        error
                    }
                }
            }
        });
    });

    it('should render the manifest viewer if resource status is SUCCESS', () =>
    {
        const resource = new ManifestResource({
            id: uuid,
            status: SUCCESS,
            value: new ManifestResource.ValueClass({
                manifest: manifestObject
            })
        });

        const output = shallowRender(<ManifestDisplay manifestRequest={resource} />);

        expect(output).toBeObjectContaining({
            type: ManifestViewer,
            props: {
                manifest: manifestObject
            }
        });
    });
});
