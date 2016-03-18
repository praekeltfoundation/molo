import { spy } from 'sinon';
import { expect } from 'chai';
import { mount } from 'enzyme';
import React from 'react';
import fixtures from 'tests/views/git-importer/fixtures';
import ChooseLanguages from 'src/views/git-importer/components/choose-languages';


describe(`ChooseLangauges`, () => {
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
});
