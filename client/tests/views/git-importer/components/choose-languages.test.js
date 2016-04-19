import { spy } from 'sinon';
import { expect } from 'chai';
import { mount } from 'enzyme';
import React from 'react';
import fixtures from 'tests/views/git-importer/fixtures';
import ChooseLanguages from 'src/views/git-importer/components/choose-languages';


describe(`ChooseLanguages`, () => {
  it(`should render the available languages`, () => {
    const state = fixtures('git-importer');

    state.languages = [{
      id: 'en',
      name: 'English',
      isMain: true,
      isChosen: false
    }, {
      id: 'sw',
      name: 'Swahili',
      isMain: false,
      isChosen: false
    }];

    const el = mount(
      <ChooseLanguages
        site={state.site}
        status={state.status}
        actions={state.actions}
        languages={state.languages} />);

    expect(el.find('.c-choose-languages__language')
      .at(0)
      .text())
      .to.equal('English');

    expect(el.find('.c-choose-languages__language')
      .at(1)
      .text())
      .to.equal('Swahili');
  });

  it(`should call toggleLanguageChosen when user chooses a language`, () => {
    const state = fixtures('git-importer');
    state.actions.toggleLanguageChosen = spy();

    state.languages = [{
      id: 'en',
      name: 'English',
      isMain: true
    }, {
      id: 'sw',
      name: 'Swahili',
      isMain: false
    }];

    const el = mount(
      <ChooseLanguages
        site={state.site}
        status={state.status}
        actions={state.actions}
        languages={state.languages} />);

    el.find('.c-choose-languages__language')
      .find('input')
      .at(1)
      .simulate('change', {
        target: {value: true}
      });

    expect(state.actions.toggleLanguageChosen.calledOnce)
      .to.be.true;

    expect(state.actions.toggleLanguageChosen.calledWith('sw'))
      .to.be.true;
  });

  it(`should call importContent() when import button is clicked`, () => {
    const state = fixtures('git-importer');
    let importContent = state.actions.importContent = spy();

    let el = mount(
      <ChooseLanguages
        site={state.site}
        status={state.status}
        actions={state.actions}
        languages={state.languages} />);

    el.find('.c-choose-languages__import')
      .simulate('click');

    expect(importContent.calledWith(state.site.id, state.languages))
      .to.be.true;

    expect(importContent.calledOnce)
      .to.be.true;
  });

  it(`should call checkContent() when check button is clicked`, () => {
    const state = fixtures('git-importer');
    let checkContent = state.actions.checkContent = spy();

    let el = mount(
      <ChooseLanguages
        site={state.site}
        status={state.status}
        actions={state.actions}
        languages={state.languages} />);

    el.find('.c-choose-languages__check')
      .simulate('click');

    expect(checkContent.calledWith(state.site.id, state.languages))
      .to.be.true;

    expect(checkContent.calledOnce)
      .to.be.true;
  });

  it(`should change import button to a busy button when busy`, () => {
    const state = fixtures('git-importer');
    state.status = 'IDLE';

    let el = mount(
      <ChooseLanguages
        site={state.site}
        status={state.status}
        actions={state.actions}
        languages={state.languages} />);

    let button = el.find('.c-choose-languages__import');
    expect(button.text()).to.equal('Import');
    expect(button.prop('disabled')).to.be.false;

    state.status = 'IMPORT_CONTENT_BUSY';

    el = mount(
      <ChooseLanguages
        site={state.site}
        status={state.status}
        actions={state.actions}
        languages={state.languages} />);

    button = el.find('.c-choose-languages__import');
    expect(button.text()).to.equal('Importing content...');
    expect(button.prop('disabled')).to.be.true;
  });

  it(`should change import button to a completed button when complete`, () => {
    const state = fixtures('git-importer');
    state.status = 'IDLE';

    let el = mount(
      <ChooseLanguages
        site={state.site}
        status={state.status}
        actions={state.actions}
        languages={state.languages} />);

    let button = el.find('.c-choose-languages__import');
    expect(button.text()).to.equal('Import');

    state.status = 'IMPORT_CONTENT_COMPLETE';

    el = mount(
      <ChooseLanguages
        site={state.site}
        status={state.status}
        actions={state.actions}
        languages={state.languages} />);

    button = el.find('.c-choose-languages__import');
    expect(button.text()).to.equal('Import complete');
  });

  it(`should change import button to an error button on error`, () => {
    const state = fixtures('git-importer');
    state.status = 'IDLE';

    let el = mount(
      <ChooseLanguages
        site={state.site}
        status={state.status}
        actions={state.actions}
        languages={state.languages} />);

    let button = el.find('.c-choose-languages__import');
    expect(button.text()).to.equal('Import');

    state.status = 'IMPORT_CONTENT_ERROR';

    el = mount(
      <ChooseLanguages
        site={state.site}
        status={state.status}
        actions={state.actions}
        languages={state.languages} />);

    button = el.find('.c-choose-languages__import');
    expect(button.text()).to.equal('Could not import content');
  });

  it(`should disable the import button if the status is not
      IDLE or CHECK_CONTENT_COMPLETE`, () => {
    const state = fixtures('git-importer');
    state.status = 'IDLE';

    let el = mount(
      <ChooseLanguages
        site={state.site}
        status={state.status}
        actions={state.actions}
        languages={state.languages} />);

    let button = el.find('.c-choose-languages__import');
    expect(button.prop('disabled')).to.be.false;

    state.status = 'CHECK_CONTENT_COMPLETE';

    el = mount(
      <ChooseLanguages
        site={state.site}
        status={state.status}
        actions={state.actions}
        languages={state.languages} />);

    button = el.find('.c-choose-languages__import');
    expect(button.prop('disabled')).to.be.false;

    state.status = 'CHECK_CONTENT_ERROR';

    el = mount(
      <ChooseLanguages
        site={state.site}
        status={state.status}
        actions={state.actions}
        languages={state.languages} />);

    button = el.find('.c-choose-languages__import');
    expect(button.prop('disabled')).to.be.true;
  });

  it(`should change check button to a busy button when busy`, () => {
    const state = fixtures('git-importer');
    state.status = 'IDLE';

    let el = mount(
      <ChooseLanguages
        site={state.site}
        status={state.status}
        actions={state.actions}
        languages={state.languages} />);

    let button = el.find('.c-choose-languages__check');
    expect(button.text()).to.equal('Check for errors');
    expect(button.prop('disabled')).to.be.false;

    state.status = 'CHECK_CONTENT_BUSY';

    el = mount(
      <ChooseLanguages
        site={state.site}
        status={state.status}
        actions={state.actions}
        languages={state.languages} />);

    button = el.find('.c-choose-languages__check');
    expect(button.text()).to.equal('Checking for errors...');
    expect(button.prop('disabled')).to.be.true;
  });

  it(`should change check button to a completed button when complete`, () => {
    const state = fixtures('git-importer');
    state.status = 'IDLE';

    let el = mount(
      <ChooseLanguages
        site={state.site}
        status={state.status}
        actions={state.actions}
        languages={state.languages} />);

    let button = el.find('.c-choose-languages__check');
    expect(button.text()).to.equal('Check for errors');

    state.status = 'CHECK_CONTENT_COMPLETE';

    el = mount(
      <ChooseLanguages
        site={state.site}
        status={state.status}
        actions={state.actions}
        languages={state.languages} />);

    button = el.find('.c-choose-languages__check');
    expect(button.text()).to.equal('No errors found');
  });

  it(`should change check button to an error button on error`, () => {
    const state = fixtures('git-importer');
    state.status = 'IDLE';

    let el = mount(
      <ChooseLanguages
        site={state.site}
        status={state.status}
        actions={state.actions}
        languages={state.languages} />);

    let button = el.find('.c-choose-languages__check');
    expect(button.text()).to.equal('Check for errors');

    state.status = 'CHECK_CONTENT_ERROR';

    el = mount(
      <ChooseLanguages
        site={state.site}
        status={state.status}
        actions={state.actions}
        languages={state.languages} />);

    button = el.find('.c-choose-languages__check');
    expect(button.text()).to.equal('Errors found');
  });

  it(`should disable the check button if the status is not IDLE`, () => {
    const state = fixtures('git-importer');
    state.status = 'IDLE';

    let el = mount(
      <ChooseLanguages
        site={state.site}
        status={state.status}
        actions={state.actions}
        languages={state.languages} />);

    let button = el.find('.c-choose-languages__check');
    expect(button.prop('disabled')).to.be.false;

    state.status = 'CHECK_CONTENT_ERROR';

    el = mount(
      <ChooseLanguages
        site={state.site}
        status={state.status}
        actions={state.actions}
        languages={state.languages} />);

    button = el.find('.c-choose-languages__check');
    expect(button.prop('disabled')).to.be.true;
  });
});
