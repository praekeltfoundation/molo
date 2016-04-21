import { expect } from 'chai';
import * as api from 'src/views/git-importer/api';
import * as serialize from 'src/views/git-importer/api/serialize';


describe(`api`, () => {
  describe(`repos`, () => {
    it(`should return the given site's repos`, () => {
      return api.repos('http://www.00-iogt.apollo.unicore.io')
        .then(sites => expect(sites).to.deep.equal([{
          id: 'unicore-cms-content-barefootlaw-i1-prod',
          title: 'Your Rights'
        }, {
          id: 'unicore-cms-content-connectsmart-i1-prod',
          title: 'Connect Smart'
        }, {
          id: 'unicore-cms-content-ebola-i1-prod',
          title: 'Emergency Information'
        }, {
          id: 'unicore-cms-content-ecd-i1-prod',
          title: 'Early Life Tips!'
        }, {
          id: 'unicore-cms-content-ffl-i1-prod',
          title: 'Facts For Life'
        }, {
          id: 'unicore-cms-content-hiv-i1-prod',
          title: 'ALL IN'
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
          isChosen: false
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

  describe(`serialize`, () => {
    describe(`url`, () => {
      it(`should parse urls`, () => {
        expect(serialize.url('https://www.a.com:3000/b/c?d=e&f=g#h/'))
          .to.deep.equal({
            protocol: 'https',
            host: 'a.com',
            port: '3000',
            path: '/b/c'
          });
      });

      it(`should support urls without protocols`, () => {
        expect(serialize.url('www.a.com'))
          .to.deep.equal({
            protocol: 'http',
            host: 'a.com'
          });
      });

      it(`should support urls without www's or protocols`, () => {
        expect(serialize.url('a.com'))
          .to.deep.equal({
            protocol: 'http',
            host: 'a.com'
          });
      });
    });
  });
});
