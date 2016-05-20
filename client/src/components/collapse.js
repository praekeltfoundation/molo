import ReactCollapse from 'react-collapse';


export default class Collapse extends ReactCollapse {
  componentWillMount() {
    super.componentWillMount();

    // On the first render, react-collapse renders without using react-motion,
    // then uses react-motion from then on. This seems to be causing react to
    // think we are rendering a new element, rather than updating an element,
    // so `<input>`s in the collapse component will lose focus. Overriding
    // `renderStatic` makes react-collapse always use react-motion when
    // rendering.
    this.renderStatic = false;
  }
}
