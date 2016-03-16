import { expect } from 'chai';
import fixtures from 'tests/views/git-importer/fixtures';
import gitImporter from 'src/views/git-importer/reducers';
import * as actions from 'src/views/git-importer/actions';


describe(`gitImporter`, () => {
  describe(`change-site`, () => {
    it(`should change site if the site exists`, () => {
      const state = fixtures('state');

      state.data.sites = [{
        id: 'foo-id',
        name: 'foo'
      }];

      expect(gitImporter(state, actions.changeSite('bar-id')).data.site)
        .to.equal(null);

      expect(gitImporter(state, actions.changeSite('foo-id')).data.site)
        .to.deep.equal({
          id: 'foo-id',
          name: 'foo'
        });
    });
  });
});

