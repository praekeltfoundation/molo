import { spy } from 'sinon';
import { expect } from 'chai';
import { shallow } from 'enzyme';
import React from 'react';
import fixtures from 'tests/views/git-importer/fixtures';
import GitImporter from 'src/views/git-importer/components/git-importer';


describe(`GitImporter`, () => {
  it(`should render disabled and enabled steps`, () => {
    const state = fixtures('git-importer');
    state.steps.site.isDisabled = false;
    state.steps.main.isDisabled = true;

    const el = shallow(<GitImporter {...state} />);

    const site = el
      .find('.c-git-import-step--site')
      .find('.o-collapse-header');

    const main = el
      .find('.c-git-import-step--main')
      .find('.o-collapse-header');

    expect(site.prop('disabled'))
      .to.be.false;

    expect(main.prop('disabled'))
      .to.be.true;
  });

  it(`should call expandStep when user clicks on a completed step`, () => {
    const state = fixtures('git-importer');
    state.steps.main.isDisabled = false;
    state.actions.expandStep = spy();

    const el = shallow(<GitImporter {...state} />);

    el
      .find('.c-git-import-step--main')
      .find('.o-collapse-header')
      .simulate('click');

    expect(state.actions.expandStep.calledWith('main'))
      .to.be.true;

    expect(state.actions.expandStep.calledOnce)
      .to.be.true;
  });

  it(`should show an alert when an import has been started`, () => {
    const state = fixtures('git-importer');
    let el = shallow(<GitImporter {...state} />);
    expect(el.find('.c-git-import-status')).to.have.length(0);

    state.status = 'IMPORT_CONTENT_STARTED';

    el = shallow(<GitImporter {...state} />);
    const status = el.find('.c-git-import-status');

    expect(status.text())
      .to.contain(`Your import has been started`);
  });

  it(`should show an alert when checking has been started`, () => {
    const state = fixtures('git-importer');
    let el = shallow(<GitImporter {...state} />);
    expect(el.find('.c-git-import-status')).to.have.length(0);

    state.status = 'CHECK_CONTENT_STARTED';

    el = shallow(<GitImporter {...state} />);
    const status = el.find('.c-git-import-status');

    expect(status.text())
      .to.contain(`Error checking has been started`);
  });
});
