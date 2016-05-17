/* eslint-env commonjs */

const serverRegex = /^server:(.+)$/;

const serverFixture = require.context('../../tests/fixtures', true, /\.json$/);
const clientFixture = require.context('./fixtures', true, /\.json$/);

export default function getFixture(uri)
{
    const srv = serverRegex.exec(uri);

    if (srv)
        return serverFixture(`./${srv[1]}`);

    return clientFixture(`./${uri}`);
}
