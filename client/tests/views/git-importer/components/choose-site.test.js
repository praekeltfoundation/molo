import { spy } from 'sinon';
import { expect } from 'chai';
import { mount } from 'enzyme';
import React from 'react';
import fixtures from 'tests/views/git-importer/fixtures';
import ChooseSite from 'src/views/git-importer/components/choose-site';


describe(`ChooseSite`, () => {
  it(`should call changeSite when user chooses a site`, () => {
    const state = fixtures('git-importer');
    state.actions.changeSite = spy();

    state.sites = [{
      id: 'foo-id',
      name: 'foo'
    }];

    const el = mount(
      <ChooseSite
        site={state.site}
        sites={state.sites}
        actions={state.actions} />);

    el.find('.c-choose-site__search')
      .find('.o-search__input')
      .simulate('change', {
        target: {value: 'fo'}
      });

    el.find('.c-choose-site__search')
      .find('.o-search__anchor')
      .at(0)
      .simulate('click');

    expect(state.actions.changeSite.calledWith('foo-id'))
      .to.be.true;

    expect(state.actions.changeSite.calledOnce)
      .to.be.true;
  });

  it(`should disable 'Next' button if site is null`, () => {
    const state = fixtures('git-importer');
    state.site = null;

    let el = mount(
      <ChooseSite
        site={state.site}
        sites={state.sites}
        actions={state.actions} />);

    expect(el.find('.c-choose-site__next').prop('disabled'))
      .to.be.true;

    state.site = {
      id: 'foo-id',
      name: 'foo'
    };

    el = mount(
      <ChooseSite
        site={state.site}
        sites={state.sites}
        actions={state.actions} />);

    expect(el.find('.c-choose-site__next').prop('disabled'))
      .to.be.false;
  });

  it(`should call chooseSite when user clicks 'Next' button`, () => {
    const state = fixtures('git-importer');
    state.actions.chooseSite = spy();

    state.site = {
      id: 'foo-id',
      name: 'foo'
    };

    const el = mount(
      <ChooseSite
        site={state.site}
        sites={state.sites}
        actions={state.actions} />);

    el.find('.c-choose-site__next')
      .simulate('click');

    expect(state.actions.chooseSite.calledWith('foo-id'))
      .to.be.true;

    expect(state.actions.chooseSite.calledOnce)
      .to.be.true;
  });
});
