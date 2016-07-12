import { expect } from 'chai';
import * as actions from 'src/views/git-importer/actions';
import fixtures from 'tests/views/git-importer/fixtures';
import { conj } from 'src/utils';
import { captureDispatches, resolvesTo } from 'tests/utils';


describe(`actions`, () => {
  describe(`chooseSite`, done => {
    it(`should return the repos and languages to update with`, () => {
      let api = conj(fixtures('api'), {
        repos: resolvesTo({
          error: null,
          value: [{
            id: 'foo-id',
            title: 'foo'
          }, {
            id: 'bar-id',
            title: 'bar'
          }]
        }),
        languages: resolvesTo([{
          id: 'en',
          name: 'English',
          isMain: true,
          isChosen: false
        }, {
          id: 'sw',
          name: 'Swahili',
          isMain: false,
          isChosen: false
        }])
      });

      return captureDispatches(actions.chooseSite('foo.com', api))
        .then(action => expect(action).to.deep.equal([{
          type: 'CHOOSE_SITE/FETCHING_REPOS'
        }, {
          type: 'CHOOSE_SITE/FETCHING_LANGUAGES'
        }, {
          type: 'CHOOSE_SITE/DONE',
          payload: {
            repos: [{
              id: 'foo-id',
              title: 'foo'
            }, {
              id: 'bar-id',
              title: 'bar'
            }],
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
          }
        }]));
    });

    it(`should dispatch NO_REPOS_FOUND if no repos were found`, () => {
      let api = conj(fixtures('api'), {
        repos: resolvesTo({
          error: {type: 'NO_REPOS_FOUND'},
          value: null
        })
      });

      return captureDispatches(actions.chooseSite('foo.com', api))
        .then(action => expect(action).to.deep.equal([{
          type: 'CHOOSE_SITE/FETCHING_REPOS'
        }, {
          type: 'CHOOSE_SITE/NO_REPOS_FOUND'
        }]));
    });
  });

  describe(`importContent`, done => {
    it(`should dispatch BUSY and STARTED`, () => {
      let api = conj(fixtures('api'), {
        importContent: resolvesTo(null)
      });

      let {
        repos,
        languages
      } = fixtures('state');

      return captureDispatches(actions.importContent(repos, languages, api))
        .then(action => expect(action).to.deep.equal([{
          type: 'IMPORT_CONTENT/BUSY'
        }, {
          type: 'IMPORT_CONTENT/STARTED'
        }]));
    });
  });

  describe(`checkContent`, done => {
    it(`should dispatch BUSY and STARTED`, () => {
      let api = conj(fixtures('api'), {
        checkContent: resolvesTo({
          errors: [{
            type: 'foo',
            details: {bar: 'baz'}
          }]
        })
      });

      let {
        repos,
        languages
      } = fixtures('state');

      return captureDispatches(actions.checkContent(repos, languages, api))
        .then(action => expect(action).to.deep.equal([{
          type: 'CHECK_CONTENT/BUSY'
        }, {
          type: 'CHECK_CONTENT/STARTED'
        }]));
    });
  });
});
