import { expect } from 'chai';
import * as actions from 'src/views/git-importer/actions';
import fixtures from 'tests/views/git-importer/fixtures';
import { conj } from 'src/utils';
import { thunk, resolvesTo } from 'tests/utils';


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

      return thunk(actions.updateSites(api))
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

