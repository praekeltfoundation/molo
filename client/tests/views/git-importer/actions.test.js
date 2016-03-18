import { expect } from 'chai';
import * as actions from 'src/views/git-importer/actions';
import fixtures from 'tests/views/git-importer/fixtures';
import { conj } from 'src/utils';
import { doThunk, resolvesTo } from 'tests/utils';


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

      return doThunk(actions.updateSites(api))
        .then(action => expect(action).to.deep.equal({
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
        }));
      });
  });
});

describe(`chooseSite`, done => {
  it(`should return the list of sites to update with`, () => {
    let api = conj(fixtures('api'), {
      languages: resolvesTo([{
        id: 'en',
        name: 'English',
        isMain: false,
        isChosen: false
      }, {
        id: 'sw',
        name: 'Swahili',
        isMain: false,
        isChosen: false
      }])
    });

    return doThunk(actions.chooseSite('foo-id', api))
      .then(action => expect(action).to.deep.equal({
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
      }));
  });
});

