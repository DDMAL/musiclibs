import expect from 'expect';
import fetchMock from 'fetch-mock';

import getFixture from '../get-fixture';

import * as ManifestAPI from '../../js/api/manifests';

describe('api/manifests', () =>
{
    const uuid = '123e4567-e89b-12d3-a456-426655440000';
    const otherUuid = '123e4567-e89b-12d3-a456-000000000000';
    const manifest = getFixture('server:manifest.json');

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

    describe('get(id: String): Promise', () =>
    {
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
});

function installFetchMock(config)
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
