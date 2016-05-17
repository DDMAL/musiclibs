import expect from 'expect';
import Im from 'immutable';

import getFixture from '../get-fixture';

import { MANIFEST_REQUEST } from '../../js/actions';
import { PENDING, SUCCESS, ERROR } from '../../js/async-request-status';
import ManifestResource from '../../js/resources/manifest-resource';
import reduceManifests from '../../js/reducers/manifests-reducer';

describe('reducers/manifests-reducer', () =>
{
    const uuid = '123e4567-e89b-12d3-a456-426655440000';
    const manifestObject = JSON.parse(getFixture('server:manifest.json'));

    it('should return an empty map on initialization', () =>
    {
        const actual = reduceManifests(undefined, { type: 'fake/arbitrary' });
        expect(actual).toBeImmutable(Im.Map());
    });

    it('should return input state on unrecognized action', () =>
    {
        const inputState = Im.Map({ uuid: {} });
        const outputState = reduceManifests(inputState, { type: 'fake/command' });
        expect(outputState).toBeImmutable(inputState);
    });

    describe('Handling MANIFEST_REQUEST action', () =>
    {
        // FIXME(wabain): What should happen if the entry already exists?
        it('should add an entry for resource if status PENDING', () =>
        {
            const action = {
                type: MANIFEST_REQUEST,
                payload: {
                    status: PENDING,
                    id: uuid
                }
            };

            const outputState = reduceManifests(Im.Map(), action);

            expect(outputState).toBeImmutable(
                Im.Map({
                    [uuid]: new ManifestResource({
                        id: uuid,
                        status: PENDING
                    })
                })
            );
        });

        it("should update resource's remoteManifestLoaded and value.manifest if status SUCCESS", () =>
        {
            const action = {
                type: MANIFEST_REQUEST,
                payload: {
                    status: SUCCESS,
                    id: uuid,
                    manifest: manifestObject
                }
            };

            const outputState = reduceManifests(Im.Map(), action);

            expect(outputState).toBeImmutable(
                Im.Map({
                    [uuid]: new ManifestResource({
                        id: uuid,
                        status: SUCCESS,
                        remoteManifestLoaded: true,
                        value: new ManifestResource.ValueClass({
                            id: uuid,
                            manifest: manifestObject
                        })
                    })
                })
            );
        });

        it('should resource status to error if status ERROR', () =>
        {
            const error = new Error('Something done broke');
            const action = {
                type: MANIFEST_REQUEST,
                payload: {
                    status: ERROR,
                    id: uuid,
                    error
                }
            };

            const inputState = Im.Map({
                [uuid]: new ManifestResource({
                    id: uuid,
                    status: PENDING
                })
            });

            const outputState = reduceManifests(inputState, action);

            expect(outputState).toBeImmutable(
                Im.Map({
                    [uuid]: new ManifestResource({
                        id: uuid,
                        status: ERROR,
                        error
                    })
                })
            );
        });
    });
});
