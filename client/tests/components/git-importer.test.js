import { expect } from 'chai';
import { shallow } from 'enzyme';
import React from 'react';
import fixtures from '../fixtures/git-importer';
import GitImporter from '../../src/components/git-importer';


describe(`GitImporter`, () => {
  it(`should render`, () => {
    const el = shallow(<GitImporter {...fixtures('props')} />);

    expect(el.find('.c-importer__locale')
      .at(0)
      .text())
      .to.equal('en_ZA');
  });
});
