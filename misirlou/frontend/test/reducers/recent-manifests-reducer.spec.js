import expect from 'expect';
import Im from 'immutable';

import getFixture from '../get-fixture';

import { PENDING, SUCCESS, ERROR } from '../../js/async-request-status'; // eslint-disable-line no-unused-vars
import { RECENT_MANIFESTS_REQUEST } from '../../js/actions';
import RecentManifestsResource from '../../js/resources/recent-manifests-resource';
import reduceRecentManifests from '../../js/reducers/recent-manifests-reducer';

describe('reducers/recent-manifests-reducer', () =>
{
    it.skip('should do normal reducer things');

    describe('Handling RECENT_MANIFESTS_REQUEST action', () =>
    {
        const recentManifests = JSON.parse(getFixture('server:recent_manifests.json')).results;

        it('should set the manifest list given status SUCCESS', () =>
        {
            const action = {
                type: RECENT_MANIFESTS_REQUEST,
                payload: {
                    status: SUCCESS,
                    resource: recentManifests
                }
            };

            expect(reduceRecentManifests(undefined, action)).toBeImmutable(new RecentManifestsResource({
                status: SUCCESS,
                value: new RecentManifestsResource.ValueClass({
                    list: Im.List(recentManifests)
                })
            }));
        });

        it.skip('should update resource status given PENDING');
        it.skip('should update resource status given ERROR');
    });
});
