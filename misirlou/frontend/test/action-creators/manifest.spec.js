import expect, { spyOn, restoreSpies } from 'expect';
import configureMockStore from 'redux-mock-store';
import thunk from 'redux-thunk';
import Im from 'immutable';

import getFixture from '../get-fixture';

import * as ManifestApi from '../../js/api/manifests';
import * as ManifestActions from '../../js/action-creators/manifest';
import ManifestResource from '../../js/resources/manifest-resource';
import { MANIFEST_REQUEST } from '../../js/actions';
import { PENDING, SUCCESS, ERROR } from '../../js/async-request-status';


const mockStore = configureMockStore([thunk]);

describe('action-creators/manifest', () =>
{
    describe('request({ id })', () =>
    {
        const uuid = '123e4567-e89b-12d3-a456-426655440000';
        const manifestObject = JSON.parse(getFixture('server:manifest.json'));

        afterEach(() =>
        {
            restoreSpies();
        });

        it('should do nothing if the manifest is already requested and did not error', () =>
        {
            const inputState = Im.Map({
                [uuid]: new ManifestResource({
                    id: uuid,
                    status: SUCCESS,
                    value: new ManifestResource.ValueClass({
                        id: uuid,
                        manifest: manifestObject
                    })
                })
            });

            const store = mockStore({ manifests: inputState });

            expect(store.dispatch(ManifestActions.request({ id: uuid }))).toBe(null);
            expect(store.getActions()).toEqual([]);
        });

        it('should dispatch PENDING, SUCCESS on request success', () =>
        {
            const actions = [
                { type: MANIFEST_REQUEST, payload: { status: PENDING, id: uuid } },
                { type: MANIFEST_REQUEST, payload: { status: SUCCESS, id: uuid, manifest: manifestObject } }
            ];

            const store = mockStore({ manifests: Im.Map() });
            const deferred = getDeferred();

            spyOn(ManifestApi, 'get').andReturn(deferred.promise);

            const dispatchPromise = store.dispatch(ManifestActions.request({ id: uuid }));

            expect(store.getActions()).toEqual(actions.slice(0, 1));
            deferred.resolve(manifestObject);

            return dispatchPromise.then(() =>
            {
                expect(store.getActions()).toEqual(actions);
            });
        });

        it('should dispatch PENDING, ERROR on request error', () =>
        {
            const error = new Error('Something broke');
            const actions = [
                { type: MANIFEST_REQUEST, payload: { status: PENDING, id: uuid } },
                { type: MANIFEST_REQUEST, payload: { status: ERROR, id: uuid, error } }
            ];

            const store = mockStore({ manifests: Im.Map() });
            const deferred = getDeferred();

            spyOn(ManifestApi, 'get').andReturn(deferred.promise);

            const dispatchPromise = store.dispatch(ManifestActions.request({ id: uuid }));

            expect(store.getActions()).toEqual(actions.slice(0, 1));
            deferred.reject(error);

            return dispatchPromise.then(() =>
            {
                expect(store.getActions()).toEqual(actions);
            });
        });
    });
});

function getDeferred()
{
    const deferred = {};

    deferred.promise = new Promise((resolve, reject) =>
    {
        deferred.resolve = resolve;
        deferred.reject = reject;
    });

    return deferred;
}
