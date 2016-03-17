import { expect } from 'chai';
import * as api from 'src/views/git-importer/api';
import { API_PREFIX } from 'tests/consts';


describe(`api`, () => {
  describe(`sites`, () => {
    it(`return the available sites`, () => {
      return api.sites({prefix: API_PREFIX})
        .then(sites => expect(sites).to.deep.equal([{
          id: 'unicore-cms-content-barefootlaw-i1-prod',
          name: 'unicore-cms-content-barefootlaw-i1-prod'
        }, {
          id: 'unicore-cms-content-ffl-sn-prod',
          name: 'unicore-cms-content-ffl-sn-prod'
        }]));
    });
  });
});

