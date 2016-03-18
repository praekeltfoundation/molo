import { expect } from 'chai';
import * as api from 'src/views/git-importer/api';
import { API_PREFIX } from 'tests/consts';


describe(`api`, () => {
  describe(`sites`, () => {
    it(`should return the available sites`, () => {
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

  describe(`languages`, () => {
    it(`should return the given site's available languages`, () => {
      return api.languages('unicore-cms-content-ffl-sn-prod', {
          prefix: API_PREFIX
        })
        .then(sites => expect(sites).to.deep.equal([{
          id: 'fre_FR',
          name: 'French (France)',
          isMain: true,
          isChosen: false
        }, {
          id: 'eng_GB',
          name: 'English (United Kingdom)',
          isMain: false,
          isChosen: false
        }]));
    });
  });
});

