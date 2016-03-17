import { expect } from 'chai';
import * as actions from 'src/views/git-importer/actions';
import fixtures from 'tests/views/git-importer/fixtures';
import { conj } from 'src/utils';
import { resolvesTo } from 'tests/utils';


describe(`actions`, () => {
  describe(`updateSites`, done => {
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

      actions.updateSites(api)(action => {
        expect(action).to.deep.equal({
          type: 'update-sites',
          sites: [{
            id: 'foo-id',
            name: 'foo'
          }, {
            id: 'bar-id',
            name: 'bar'
          }]
        });

        done();
      });
    });
  });
});

