import { spy } from 'sinon';
import { expect } from 'chai';
import { mount } from 'enzyme';
import React from 'react';
import fixtures from 'tests/views/git-importer/fixtures';
import ChooseSite from 'src/views/git-importer/components/choose-site';


function draw(state) {
  return mount(
    <ChooseSite
      status={state.status}
      siteUrl={state.siteUrl}
      repos={state.repos}
      actions={state.actions} />
  );
}


describe(`ChooseSite`, () => {
  it(`should call changeSiteUrl when user changes site url`, () => {
    const state = fixtures('git-importer');
    state.actions.changeSiteUrl = spy();

    state.siteUrl = 'foo.com';

    let el = draw(state);

    el.find('.c-choose-site__input')
      .simulate('change', {
        target: {value: 'bar.com'}
      });

    expect(state.actions.changeSiteUrl.calledWith('bar.com'))
      .to.be.true;

    expect(state.actions.changeSiteUrl.calledOnce)
      .to.be.true;
  });

  it(`should change 'Next' button to a busy button when busy`, () => {
    const state = fixtures('git-importer');
    state.status = 'IDLE';

    let el = draw(state);
    let button = el.find('.c-choose-site__next');
    expect(button.text()).to.equal('Next');
    expect(button.prop('disabled')).to.be.false;

    state.status = 'CHOOSE_SITE_BUSY';

    el = mount(
      <ChooseSite
        status={state.status}
        site={state.site}
        sites={state.sites}
        actions={state.actions} />);

    button = el.find('.c-choose-site__next');
    expect(button.text()).to.equal('Fetching languages...');
    expect(button.prop('disabled')).to.be.true;
  });

  it(`should disable 'Next' button if siteUrl is null`, () => {
    const state = fixtures('git-importer');
    state.siteUrl = null;

    let el = draw(state);

    expect(el.find('.c-choose-site__next').prop('disabled'))
      .to.be.true;

    state.siteUrl = 'bar.com';

    el = draw(state);

    expect(el.find('.c-choose-site__next').prop('disabled'))
      .to.be.false;
  });

  it(`should call chooseSite when user clicks 'Next' button`, () => {
    const state = fixtures('git-importer');
    state.actions.chooseSite = spy();

    state.siteUrl = 'foo.com';

    let el = draw(state);

    el.find('.c-choose-site__next')
      .simulate('click');

    expect(state.actions.chooseSite.calledWith('foo.com'))
      .to.be.true;

    expect(state.actions.chooseSite.calledOnce)
      .to.be.true;
  });
});
