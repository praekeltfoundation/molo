import { expect } from 'chai';
import React from 'react';
import ReactDOM from 'react-dom';
import TestUtils from 'react-addons-test-utils';
import GitImporter from '../../src/components/git-importer';


describe(`GitImporter`, () => {
  it(`should render`, () => {
    const component = TestUtils.renderIntoDocument(
      <GitImporter/>
    );

    const el = ReactDOM.findDOMNode(component);

    expect(el.textContent).to.equal('TODO');
  });
});
