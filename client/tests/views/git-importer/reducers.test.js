import { expect } from 'chai';
import fixtures from 'tests/views/git-importer/fixtures';
import gitImporter from 'src/views/git-importer/reducers';
import { conj } from 'src/utils';


describe(`gitImporter`, () => {
  describe(`expand-step`, () => {
    it(`should change the current step`, () => {
      const state = fixtures('state');
      state.ui.currentStep = 'main';

      expect(gitImporter(state, {
          type: 'expand-step',
          name: 'site'
        }))
        .to.deep.equal(conj(fixtures('state'), {
          ui: conj(state.ui, {
            currentStep: 'site'
          })
        }));
    });
  });

  describe(`choose-site`, () => {
    it("should change the current and last steps to 'main'", () => {
      const state = fixtures('state');
      state.ui.currentStep = 'site';
      state.ui.lastStep = 'site';

      expect(gitImporter(state, {type: 'choose-site'}))
        .to.deep.equal(conj(fixtures('state'), {
          ui: conj(state.ui, {
            currentStep: 'main',
            lastStep: 'main'
          })
        }));
    });
  });

  describe(`choose-main`, () => {
    it("should change the current and last steps to 'languages'", () => {
      const state = fixtures('state');
      state.ui.currentStep = 'main';
      state.ui.lastStep = 'main';

      expect(gitImporter(state, {type: 'choose-main'}))
        .to.deep.equal(conj(fixtures('state'), {
          ui: conj(state.ui, {
            currentStep: 'languages',
            lastStep: 'languages'
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

      expect(gitImporter(state, {
          id: 'bar-id',
          type: 'change-site'
        }))
        .to.deep.equal(conj(fixtures('state'), {
          data: conj(state.data, {
            site: null
          })
        }));

      expect(gitImporter(state, {
          id: 'foo-id',
          type: 'change-site'
        }))
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
        isMain: true,
        isChosen: false
      }, {
        id: 'sw',
        name: 'Swahili',
        isMain: false,
        isChosen: false
      }];

      expect(gitImporter(state, {
          type: 'change-main',
          id: 'sw'
        }))
        .to.deep.equal(conj(fixtures('state'), {
          data: conj(state.data, {
            languages: [{
              id: 'en',
              name: 'English',
              isMain: false,
              isChosen: false
            }, {
              id: 'sw',
              name: 'Swahili',
              isMain: true,
              isChosen: false
            }]
          })
        }));
    });
  });

  describe(`toggle-language-chosen`, () => {
    it(`should choose/unchoose the language`, () => {
      const state = fixtures('state');

      state.data.languages = [{
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

      expect(gitImporter(state, {
          type: 'toggle-language-chosen',
          id: 'sw'
        }))
        .to.deep.equal(conj(fixtures('state'), {
          data: conj(state.data, {
            languages: [{
              id: 'en',
              name: 'English',
              isMain: true,
              isChosen: false
            }, {
              id: 'sw',
              name: 'Swahili',
              isMain: false,
              isChosen: true
            }]
          })
        }));

      state.data.languages = [{
        id: 'en',
        name: 'English',
        isMain: true,
        isChosen: false
      }, {
        id: 'sw',
        name: 'Swahili',
        isMain: false,
        isChosen: true
      }];

      expect(gitImporter(state, {
          type: 'toggle-language-chosen',
          id: 'sw'
        }))
        .to.deep.equal(conj(fixtures('state'), {
          data: conj(state.data, {
            languages: [{
              id: 'en',
              name: 'English',
              isMain: true,
              isChosen: false
            }, {
              id: 'sw',
              name: 'Swahili',
              isMain: false,
              isChosen: false
            }]
          })
        }));
    });
  });
});

