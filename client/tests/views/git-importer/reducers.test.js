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

  describe(`CHOOSE_SITE/FETCHING_REPOS`, () => {
    it(`should change the ui status to CHOOSE_SITE_FETCHING_REPOS`, () => {
      const state = fixtures('state');
      state.ui.status = 'IDLE';

      expect(gitImporter(state, {
          type: 'CHOOSE_SITE/FETCHING_REPOS'
        }))
        .to.deep.equal(conj(fixtures('state'), {
          ui: conj(state.ui, {
            status: 'CHOOSE_SITE_FETCHING_REPOS'
          })
        }));
    });
  });

  describe(`CHOOSE_SITE/FETCHING_LANGUAGES`, () => {
    it(`should change the ui status to CHOOSE_SITE_FETCHING_LANGUAGES`, () => {
      const state = fixtures('state');
      state.ui.status = 'IDLE';

      expect(gitImporter(state, {
          type: 'CHOOSE_SITE/FETCHING_LANGUAGES'
        }))
        .to.deep.equal(conj(fixtures('state'), {
          ui: conj(state.ui, {
            status: 'CHOOSE_SITE_FETCHING_LANGUAGES'
          })
        }));
    });
  });

  describe(`CHOOSE_SITE/NO_REPOS_FOUND`, () => {
    it(`should change the ui status to CHOOSE_SITE_NO_REPOS_FOUND`, () => {
      const state = fixtures('state');
      state.ui.status = 'IDLE';

      expect(gitImporter(state, {
          type: 'CHOOSE_SITE/NO_REPOS_FOUND'
        }))
        .to.deep.equal(conj(fixtures('state'), {
          ui: conj(state.ui, {
            status: 'CHOOSE_SITE_NO_REPOS_FOUND'
          })
        }));
    });
  });

  describe(`CHOOSE_SITE/INVALID_URL`, () => {
    it(`should change the ui status to CHOOSE_SITE_INVALID_URL`, () => {
      const state = fixtures('state');
      state.ui.status = 'IDLE';

      expect(gitImporter(state, {
          type: 'CHOOSE_SITE/INVALID_URL'
        }))
        .to.deep.equal(conj(fixtures('state'), {
          ui: conj(state.ui, {
            status: 'CHOOSE_SITE_INVALID_URL'
          })
        }));
    });
  });

  describe(`CHOOSE_SITE/DONE`, () => {
    it("should change the current and last steps to 'main'", () => {
      const state = fixtures('state');
      state.ui.currentStep = 'site';
      state.ui.lastStep = 'site';
      state.ui.status = 'CHOOSE_SITE_BUSY';

      expect(gitImporter(state, {
          type: 'CHOOSE_SITE/DONE',
          payload: {
            repos: [{
              id: 'foo-id',
              name: 'foo'
            }, {
              id: 'bar-id',
              name: 'bar'
            }],
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
            lastStep: 'main',
            status: 'IDLE'
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

      expect(gitImporter(state, {type: 'CHOOSE_MAIN'}).ui)
        .to.deep.equal(conj(fixtures('state').ui, {
          currentStep: 'languages',
          lastStep: 'languages'
        }));
    });

    it("should set the chosen main language as a chosen language", () => {
      const state = fixtures('state');

      state.data.languages = [{
        id: 'en',
        name: 'English',
        isMain: false,
        isChosen: false
      }, {
        id: 'sw',
        name: 'Swahili',
        isMain: true,
        isChosen: false
      }];

      expect(gitImporter(state, {type: 'CHOOSE_MAIN'}).data)
        .to.deep.equal(conj(fixtures('state').data, {
          languages: [{
            id: 'en',
            name: 'English',
            isMain: false,
            isChosen: false
          }, {
            id: 'sw',
            name: 'Swahili',
            isMain: true,
            isChosen: true
          }]
        }));
    });
  });

  describe(`CHANGE_SITE_URL`, () => {
    it(`should update the site url`, () => {
      const state = fixtures('state');

      expect(gitImporter(fixtures('state'), {
          type: 'CHANGE_SITE_URL',
          payload: {url: 'foo.com'}
        }))
        .to.deep.equal(conj(state, {
          data: conj(state.data, {
            siteUrl: 'foo.com'
          })
        }));
    });

    it(`should change the ui status to IDLE`, () => {
      const state = fixtures('state');

      expect(gitImporter(fixtures('state'), {
          type: 'CHANGE_SITE_URL',
          payload: {url: 'foo.com'}
        }))
        .to.deep.equal(conj(state, {
          ui: conj(state.ui, {
            status: 'IDLE'
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

  describe(`IMPORT_CONTENT/BUSY`, () => {
    it("should change the ui state to busy", () => {
      const state = fixtures('state');
      state.ui.status = 'IDLE';

      expect(gitImporter(state, {
          type: 'IMPORT_CONTENT/BUSY'
        }))
        .to.deep.equal(conj(fixtures('state'), {
          ui: conj(state.ui, {
            status: 'IMPORT_CONTENT_BUSY'
          })
        }));
    });
  });

  describe(`IMPORT_CONTENT/STARTED`, () => {
    it("should set the status to started", () => {
      const state = fixtures('state');
      state.ui.status = 'IMPORT_CONTENT_STARTED';

      expect(gitImporter(state, {
          type: 'IMPORT_CONTENT/STARTED'
        }))
        .to.deep.equal(conj(fixtures('state'), {
          ui: conj(state.ui, {
            status: 'IMPORT_CONTENT_STARTED'
          })
        }));
    });
  });

  describe(`CHECK_CONTENT/BUSY`, () => {
    it("should change the ui state to busy", () => {
      const state = fixtures('state');
      state.ui.status = 'IDLE';

      expect(gitImporter(state, {
          type: 'CHECK_CONTENT/BUSY'
        }))
        .to.deep.equal(conj(fixtures('state'), {
          ui: conj(state.ui, {
            status: 'CHECK_CONTENT_BUSY'
          })
        }));
    });
  });

  describe(`CHECK_CONTENT/STARTED`, () => {
    it("should set the status to started", () => {
      const state = fixtures('state');
      state.ui.status = 'CHECK_CONTENT_BUSY';

      expect(gitImporter(state, {
          type: 'CHECK_CONTENT/STARTED'
        }))
        .to.deep.equal(conj(fixtures('state'), {
          ui: conj(state.ui, {
            status: 'CHECK_CONTENT_STARTED'
          })
        }));
    });
  });
});

