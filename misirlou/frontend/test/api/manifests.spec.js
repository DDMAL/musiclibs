import expect from 'expect';
import fetchMock from 'fetch-mock';

import getFixture from '../get-fixture';

import * as ManifestAPI from '../../js/api/manifests';

describe('api/manifests', () =>
{
    describe('get(id: String): Promise', () =>
    {
        const manifest = getFixture('server:manifest.json');
        const uuid = '123e4567-e89b-12d3-a456-426655440000';
        const otherUuid = '123e4567-e89b-12d3-a456-000000000000';

        installFetchMock([
            {
                matcher: `/manifests/${uuid}/`,
                method: 'GET',
                response: {
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: manifest
                }
            }
        ]);

        it('should fetch manifests from the /manifests/:id/ endpoint', () =>
        {
            return ManifestAPI.get(uuid).then((fetched) =>
            {
                expect(fetched).toEqual(JSON.parse(manifest));
            });
        });

        it('should throw RequestFailureError on non-200 responses', () =>
        {
            fetchMock.mock(`/manifests/${otherUuid}/`, 'GET', {
                status: 201,
                body: manifest
            });

            return ManifestAPI.get(otherUuid).then(() =>
            {
                throw new Error('Did not throw');
            }, (error) =>
            {
                expect(error.name).toBe('RequestFailureError');
                expect(error.message).toMatch(/Created/);
            });
        });
    });

    describe('getRecent(): Promise', () =>
    {
        const recentManifests = getFixture('server:recent_manifests.json');

        installFetchMock();

        it('should fetch the recent manifests list from the /manifests/recent/ endpoint', () =>
        {
            fetchMock.mock('/manifests/recent/', 'GET', {
                status: 200,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: recentManifests
            });

            return ManifestAPI.getRecent().then((fetched) =>
            {
                expect(fetched).toEqual(JSON.parse(recentManifests));
            });
        });

        it('should throw RequestFailureError on non-200 responses', () =>
        {
            fetchMock.mock('/manifests/recent/', 'GET', {
                status: 201,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: recentManifests
            });

            return ManifestAPI.getRecent().then(() =>
            {
                throw new Error('Did not throw');
            }, (error) =>
            {
                expect(error.name).toBe('RequestFailureError');
                expect(error.message).toMatch(/Created/);
            });
        });
    });
});

function installFetchMock(config = [])
{
    beforeEach(() =>
    {
        fetchMock.reMock(config);
    });

    afterEach(() =>
    {
        if (fetchMock.calls().unmatched.length > 0)
            throw new Error(`Unhandled fetch: ${fetchMock.calls().unmatched.map(JSON.stringify).join()}`);
    });

    after(() =>
    {
        fetchMock.restore();
    });
}
