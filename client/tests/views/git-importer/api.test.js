import { expect } from 'chai';
import * as api from 'src/views/git-importer/api';


describe(`api`, () => {
  describe(`sites`, () => {
    it(`should return the available sites`, () => {
      return api.sites()
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
      return api.languages('unicore-cms-content-ffl-sn-prod')
        .then(sites => expect(sites).to.deep.equal([{
          id: 'fre_FR',
          name: 'French (France)',
          isMain: true,
          isChosen: true
        }, {
          id: 'eng_GB',
          name: 'English (United Kingdom)',
          isMain: false,
          isChosen: false
        }]));
    });
  });

  describe(`importContent`, () => {
    it(`should import content for the chosen langauges`, () => {
      return api.importContent('unicore-cms-content-ffl-sn-prod', [{
          id: 'fre_FR',
          name: 'French (France)',
          isMain: true,
          isChosen: true
        }, {
          id: 'eng_GB',
          name: 'English (United Kingdom)',
          isMain: false,
          isChosen: true
        }])
        .then(sites => expect(sites).to.deep.equal({
          errors: []
        }));
    });

    it(`should return validation errors`, () => {
      return api.importContent('unicore-cms-content-mama-mx-prod', [{
          id: 'spa_MX',
          name: 'Spanish (Mexico)',
          isMain:true,
          isChosen:true
        }, {
          id: 'eng_GB',
          name: 'English (United Kingdom)',
          isMain:false,
          isChosen:false
        },{
          id: 'spa_ES',
          name: 'Spanish (Spain)',
          isMain:false,
          isChosen:true
        }])
        .then(sites => expect(sites).to.deep.equal({
          errors: [{
            type: 'wrong_main_language_exist_in_wagtail',
            details: {
              lang: 'French',
              selected_lang: 'Spanish (Mexico)'
            }
          }, {
            type: 'no_primary_category',
            details: {
              lang: 'Spanish (Mexico)',
              article: 'Palabras sobre el embarazo y el parto'
            }
          }]
        }));
    });
  });

  describe(`checkContent`, () => {
    it(`should check content for the chosen langauges`, () => {
      return api.checkContent('unicore-cms-content-ffl-sn-prod', [{
          id: 'fre_FR',
          name: 'French (France)',
          isMain: true,
          isChosen: true
        }, {
          id: 'eng_GB',
          name: 'English (United Kingdom)',
          isMain: false,
          isChosen: true
        }])
        .then(sites => expect(sites).to.deep.equal({
          errors: []
        }));
    });

    it(`should return validation errors`, () => {
      return api.checkContent('unicore-cms-content-mama-mx-prod', [{
          id: 'spa_MX',
          name: 'Spanish (Mexico)',
          isMain:true,
          isChosen:true
        }, {
          id: 'eng_GB',
          name: 'English (United Kingdom)',
          isMain:false,
          isChosen:false
        },{
          id: 'spa_ES',
          name: 'Spanish (Spain)',
          isMain:false,
          isChosen:true
        }])
        .then(sites => expect(sites).to.deep.equal({
          errors: [{
            type: 'wrong_main_language_exist_in_wagtail',
            details: {
              lang: 'French',
              selected_lang: 'Spanish (Mexico)'
            }
          }, {
            type: 'no_primary_category',
            details: {
              lang: 'Spanish (Mexico)',
              article: 'Palabras sobre el embarazo y el parto'
            }
          }]
        }));
    });
  });
});

