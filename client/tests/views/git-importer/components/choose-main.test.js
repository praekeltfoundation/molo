import { spy } from 'sinon';
import { expect } from 'chai';
import { mount } from 'enzyme';
import React from 'react';
import fixtures from 'tests/views/git-importer/fixtures';
import ChooseMain from 'src/views/git-importer/components/choose-main';


describe(`ChooseMain`, () => {
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
      <ChooseMain
        actions={state.actions}
        languages={state.languages} />);

    expect(el.find('.c-choose-main__language')
      .at(0)
      .text())
      .to.equal('English');

    expect(el.find('.c-choose-main__language')
      .at(1)
      .text())
      .to.equal('Swahili');
  });

  it(`should call changeMain when user chooses a main language`, () => {
    const state = fixtures('git-importer');
    state.actions.changeMain = spy();

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
      <ChooseMain
        actions={state.actions}
        languages={state.languages} />);

    el.find('.c-choose-main__language')
      .find('input')
      .at(0)
      .simulate('change', {
        target: {value: true}
      });

    expect(state.actions.changeMain.calledOnce)
      .to.be.true;

    expect(state.actions.changeMain.calledWith('en'))
      .to.be.true;
  });
});
