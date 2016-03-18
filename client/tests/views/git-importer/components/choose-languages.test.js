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

  it(`should call importContent() when 'Import' button is clicked`, () => {
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

  it(`should change 'Import' button to a loading button when loading`, () => {
    const state = fixtures('git-importer');
    state.status = 'IDLE';

    let el = mount(
      <ChooseLanguages
        site={state.site}
        status={state.status}
        actions={state.actions}
        languages={state.languages} />);

    let button = el.find('.c-choose-languages__import');
    expect(button.text()).to.equal('Import content');
    expect(button.prop('disabled')).to.be.false;

    state.status = 'LOADING';

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

  it(`should change 'Import' button to a completed button when complete`, () => {
    const state = fixtures('git-importer');
    state.status = 'IDLE';

    let el = mount(
      <ChooseLanguages
        site={state.site}
        status={state.status}
        actions={state.actions}
        languages={state.languages} />);

    let button = el.find('.c-choose-languages__import');
    expect(button.text()).to.equal('Import content');

    state.status = 'COMPLETE';

    el = mount(
      <ChooseLanguages
        site={state.site}
        status={state.status}
        actions={state.actions}
        languages={state.languages} />);

    button = el.find('.c-choose-languages__import');
    expect(button.text()).to.equal('Import complete');
  });
});
