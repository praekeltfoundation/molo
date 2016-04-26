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

  it(`should change 'Next' button to a busy button when fetching repos`, () => {
    const state = fixtures('git-importer');
    state.status = 'IDLE';

    let el = draw(state);
    let button = el.find('.c-choose-site__next');
    expect(button.text()).to.equal('Next');
    expect(button.prop('disabled')).to.be.false;

    state.status = 'CHOOSE_SITE_FETCHING_REPOS';

    el = draw(state);
    button = el.find('.c-choose-site__next');
    expect(button.text()).to.equal('Fetching repos...');
    expect(button.prop('disabled')).to.be.true;
  });

  it(`should change 'Next' button to a busy button when fetching languages`,
  () => {
    const state = fixtures('git-importer');
    state.status = 'IDLE';

    let el = draw(state);
    let button = el.find('.c-choose-site__next');
    expect(button.text()).to.equal('Next');
    expect(button.prop('disabled')).to.be.false;

    state.status = 'CHOOSE_SITE_FETCHING_LANGUAGES';

    el = draw(state);
    button = el.find('.c-choose-site__next');
    expect(button.text()).to.equal('Fetching languages...');
    expect(button.prop('disabled')).to.be.true;
  });

  it(`should disable 'Next' button if siteUrl is empty`, () => {
    const state = fixtures('git-importer');
    state.siteUrl = '';

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

  it(`should show an error when no repos were found for a url`, () => {
    const state = fixtures('git-importer');
    state.status = 'IDLE';

    let el = draw(state);
    let error = el.find('.c-choose-site__input_error');
    expect(error).to.have.length(0);

    state.status = 'CHOOSE_SITE_NO_REPOS_FOUND';
    el = draw(state);

    error = el.find('.c-choose-site__input-error');
    expect(error).to.have.length(1);
    expect(error.text()).to.equal(
      `No content repositories were found for this site`);
  });

  it(`should show an error when an invalid url is given`, () => {
    const state = fixtures('git-importer');
    state.status = 'IDLE';

    let el = draw(state);
    let error = el.find('.c-choose-site__input_error');
    expect(error).to.have.length(0);

    state.status = 'CHOOSE_SITE_INVALID_URL';
    el = draw(state);

    error = el.find('.c-choose-site__input-error');
    expect(error).to.have.length(1);
    expect(error.text()).to.equal(
      `Please enter a valid url (e.g. foo.bar.unicore.io)`);
  });
});
