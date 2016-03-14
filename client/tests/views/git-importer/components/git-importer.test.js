import { spy } from 'sinon';
import { expect } from 'chai';
import { shallow } from 'enzyme';
import React from 'react';
import fixtures from 'tests/views/git-importer/fixtures';
import GitImporter from 'src/views/git-importer/components/git-importer';


describe(`GitImporter`, () => {
  it(`should render`, () => {
    const el = shallow(<GitImporter {...fixtures('component:input')} />);

    expect(el.find('.c-git-importer__locale')
      .at(0)
      .text())
      .to.equal('en_ZA');
  });

  it(`should call fetchContent when fetch is clicked`, () => {
    const state = fixtures('component:input');
    state.actions.fetchContent = spy();
    const el = shallow(<GitImporter {...state} />);

    el.find('.c-git-importer__fetch')
      .simulate('click');

    expect(state.actions.fetchContent.calledOnce)
      .to.be.true;
  });
});
