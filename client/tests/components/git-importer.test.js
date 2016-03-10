import { expect } from 'chai';
import { shallow } from 'enzyme';
import React from 'react';
import GitImporter from '../../src/components/git-importer';


describe(`GitImporter`, () => {
  it(`should render`, () => {
    const el = shallow(<GitImporter stub='TODO' />);
    expect(el.text()).to.equal('TODO');
  });
});
