import { spy } from 'sinon';
import { expect } from 'chai';
import { shallow } from 'enzyme';
import React from 'react';
import fixtures from 'tests/views/git-importer/fixtures';
import GitImporter from 'src/views/git-importer/components/git-importer';


describe(`GitImporter`, () => {
  it(`should render`, () => {
    const el = shallow(<GitImporter {...fixtures('component:input')} />);

    expect(el.find('.c-git-importer__language').at(0).text())
      .to.equal('English');

    expect(el.find('.c-git-importer__language').at(1).text())
      .to.equal('Swahili');
  });

  it(`should call fetchSite when user has chosen a site`, () => {
    const state = fixtures('component:input');
    state.actions.fetchSite = spy();
    const el = shallow(<GitImporter {...state} />);

    el.find('.c-git-importer__choose-site')
      .simulate('click');

    expect(state.actions.fetchSite.calledOnce)
      .to.be.true;
  });
});
