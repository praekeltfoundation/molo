import { expect } from 'chai';
import fixtures from 'tests/views/git-importer/fixtures';
import gitImporter from 'src/views/git-importer/reducers';
import * as actions from 'src/views/git-importer/actions';
import { conj } from 'src/utils';


describe(`gitImporter`, () => {
  describe(`expand-step`, () => {
    it(`should change the current step`, () => {
      const state = fixtures('state');
      state.ui.currentStep = 'main';

      expect(gitImporter(state, actions.expandStep('site')))
        .to.deep.equal(conj(fixtures('state'), {
          ui: conj(state.ui, {
            currentStep: 'site'
          })
        }));
    });
  });

  describe(`change-site`, () => {
    it(`should change site if the site exists`, () => {
      const state = fixtures('state');

      state.data.sites = [{
        id: 'foo-id',
        name: 'foo'
      }];

      expect(gitImporter(state, actions.changeSite('bar-id')))
        .to.deep.equal(conj(fixtures('state'), {
          data: conj(state.data, {
            site: null
          })
        }));

      expect(gitImporter(state, actions.changeSite('foo-id')))
        .to.deep.equal(conj(fixtures('state'), {
          data: conj(state.data, {
            site: {
              id: 'foo-id',
              name: 'foo'
            }
          })
        }));
    });
  });

  describe(`change-main`, () => {
    it(`should change the main language`, () => {
      const state = fixtures('state');

      state.data.languages = [{
        id: 'en',
        name: 'English',
        isMain: true
      }, {
        id: 'sw',
        name: 'Swahili',
        isMain: false
      }];

      expect(gitImporter(state, actions.changeMain('sw')))
        .to.deep.equal(conj(fixtures('state'), {
          data: conj(state.data, {
            languages: [{
              id: 'en',
              name: 'English',
              isMain: false
            }, {
              id: 'sw',
              name: 'Swahili',
              isMain: true
            }]
          })
        }));
    });
  });
});

