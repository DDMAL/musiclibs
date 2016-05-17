import { createRenderer as createShallowRenderer } from 'react-addons-test-utils';

export default function shallowRender(Component)
{
    const renderer = createShallowRenderer();
    renderer.render(Component);
    return renderer.getRenderOutput();
}
