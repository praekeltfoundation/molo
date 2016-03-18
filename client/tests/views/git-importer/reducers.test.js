import { expect } from 'chai';
import fixtures from 'tests/views/git-importer/fixtures';
import gitImporter from 'src/views/git-importer/reducers';
import { conj } from 'src/utils';


describe(`gitImporter`, () => {
  describe(`EXPAND_STEP`, () => {
    it(`should change the current step`, () => {
      const state = fixtures('state');
      state.ui.currentStep = 'main';

      expect(gitImporter(state, {
          type: 'EXPAND_STEP',
          payload: {name: 'site'}
        }))
        .to.deep.equal(conj(fixtures('state'), {
          ui: conj(state.ui, {
            currentStep: 'site'
          })
        }));
    });
  });

  describe(`UPDATE_SITES`, () => {
    it(`should update the available sites`, () => {
      const state = fixtures('state');

      state.data.sites = [{
        id: 'win',
        name: 'rar'
      }];

      expect(gitImporter(state, {
          type: 'UPDATE_SITES',
          payload: {
            sites: [{
              id: 'foo-id',
              name: 'foo'
            }, {
              id: 'bar-id',
              name: 'bar'
            }]
          }
        }))
        .to.deep.equal(conj(fixtures('state'), {
          data: conj(state.data, {
            sites: [{
              id: 'foo-id',
              name: 'foo'
            }, {
              id: 'bar-id',
              name: 'bar'
            }]
          })
        }));
    });
  });

  describe(`CHOOSE_SITE`, () => {
    it("should change the current and last steps to 'main'", () => {
      const state = fixtures('state');
      state.ui.currentStep = 'site';
      state.ui.lastStep = 'site';

      expect(gitImporter(state, {
          type: 'CHOOSE_SITE',
          payload: {
            languages: [{
              id: 'en',
              name: 'English',
              isMain: false,
              isChosen: false
            }, {
              id: 'sw',
              name: 'Swahili',
              isMain: false,
              isChosen: false
            }]
          }
        }))
        .to.deep.equal(conj(fixtures('state'), {
          ui: conj(state.ui, {
            currentStep: 'main',
            lastStep: 'main'
          }),
          data: conj(state.data, {
            languages: [{
              id: 'en',
              name: 'English',
              isMain: false,
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

  describe(`CHOOSE_MAIN`, () => {
    it("should change the current and last steps to 'languages'", () => {
      const state = fixtures('state');
      state.ui.currentStep = 'main';
      state.ui.lastStep = 'main';

      expect(gitImporter(state, {type: 'CHOOSE_MAIN'}))
        .to.deep.equal(conj(fixtures('state'), {
          ui: conj(state.ui, {
            currentStep: 'languages',
            lastStep: 'languages'
          })
        }));
    });
  });

  describe(`CHANGE_SITE`, () => {
    it(`should change site if the site exists`, () => {
      const state = fixtures('state');

      state.data.sites = [{
        id: 'foo-id',
        name: 'foo'
      }];

      expect(gitImporter(state, {
          type: 'CHANGE_SITE',
          payload: {id: 'bar-id'}
        }))
        .to.deep.equal(conj(fixtures('state'), {
          data: conj(state.data, {
            site: null
          })
        }));

      expect(gitImporter(state, {
          type: 'CHANGE_SITE',
          payload: {id: 'foo-id'},
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

  describe(`CHANGE_MAIN`, () => {
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
          type: 'CHANGE_MAIN',
          payload: {id: 'sw'}
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

  describe(`TOGGLE_LANGUAGE_CHOSEN`, () => {
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
          type: 'TOGGLE_LANGUAGE_CHOSEN',
          payload: {id: 'sw'}
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
          type: 'TOGGLE_LANGUAGE_CHOSEN',
          payload: {id: 'sw'}
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

