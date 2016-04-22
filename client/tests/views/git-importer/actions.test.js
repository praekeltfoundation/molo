import { expect } from 'chai';
import * as actions from 'src/views/git-importer/actions';
import fixtures from 'tests/views/git-importer/fixtures';
import { conj } from 'src/utils';
import { captureDispatches, resolvesTo } from 'tests/utils';


describe(`actions`, () => {
  describe(`updateSites`, () => {
    it(`should return the list of sites to update with`, () => {
      let api = conj(fixtures('api'), {
        sites: resolvesTo([{
          id: 'foo-id',
          name: 'foo'
        }, {
          id: 'bar-id',
          name: 'bar'
        }])
      });

      return captureDispatches(actions.updateSites(api))
        .then(action => expect(action).to.deep.equal([{
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
        }]));
      });
  });

  describe(`chooseSite`, done => {
    it(`should return the list of sites to update with`, () => {
      let api = conj(fixtures('api'), {
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

      return captureDispatches(actions.chooseSite('foo-id', api))
        .then(action => expect(action).to.deep.equal([{
          type: 'CHOOSE_SITE/BUSY'
        }, {
          type: 'CHOOSE_SITE/DONE',
          payload: {
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
  });

  describe(`importContent`, done => {
    it(`should return errors that occured during the import`, () => {
      let api = conj(fixtures('api'), {
        importContent: resolvesTo({
          errors: [{
            type: 'foo',
            details: {bar: 'baz'}
          }]
        })
      });

      let languages = [{
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

      return captureDispatches(actions.importContent('foo-id', languages, api))
        .then(action => expect(action).to.deep.equal([{
          type: 'IMPORT_CONTENT/BUSY'
        }, {
          type: 'IMPORT_CONTENT/DONE',
          payload: {
            errors: [{
              type: 'foo',
              details: {bar: 'baz'}
            }]
          }
        }]));
    });
  });

  describe(`checkContent`, done => {
    it(`should return errors that occured during the check`, () => {
      let api = conj(fixtures('api'), {
        checkContent: resolvesTo({
          errors: [{
            type: 'foo',
            details: {bar: 'baz'}
          }]
        })
      });

      let languages = [{
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

      return captureDispatches(actions.checkContent('foo-id', languages, api))
        .then(action => expect(action).to.deep.equal([{
          type: 'CHECK_CONTENT/BUSY'
        }, {
          type: 'CHECK_CONTENT/DONE',
          payload: {
            errors: [{
              type: 'foo',
              details: {bar: 'baz'}
            }]
          }
        }]));
    });
  });
});
