import { expect } from 'chai';
import * as api from 'src/views/git-importer/api';
import * as serialize from 'src/views/git-importer/api/serialize';


describe(`api`, () => {
  describe(`repos`, () => {
    it(`should return the given site's repos`, () => {
      return api.repos('http://www.00-iogt.apollo.unicore.io')
        .then(sites => expect(sites).to.deep.equal({
          error: null,
          value: [{
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
          }]
        }));
    });

    it(`should return a NO_REPOS_FOUND error if there was a response error`,
    () => {
      return api.repos('foo.com')
        .then(sites => expect(sites)
          .to.deep.equal({
            error: {type: 'NO_REPOS_FOUND'},
            value: null
          }));
    });

    it(`should return a NO_REPOS_FOUND error if the repo list is empty`,
    () => {
      return api.repos('bar.com')
        .then(sites => expect(sites)
          .to.deep.equal({
            error: {type: 'NO_REPOS_FOUND'},
            value: null
          }));
    });
  });

  describe(`languages`, () => {
    it(`should return the given site's available languages`, () => {
      return api.languages([{
          id: 'unicore-cms-content-ffl-sn-prod',
          title: 'Facts For Life'
        }])
        .then(sites => expect(sites).to.deep.equal([{
          id: 'eng_GB',
          name: 'English (United Kingdom)',
          isMain: true,
          isChosen: false
        }, {
          id: 'fre_FR',
          name: 'French (France)',
          isMain: false,
          isChosen: false
        }]));
    });
  });

  describe(`importContent`, () => {
    it(`should import content for the chosen langauges`, () => {
      return api.importContent([{
          id: 'unicore-cms-content-ffl-sn-prod',
          title: 'Facts for Life'
        }], [{
          id: 'fre_FR',
          name: 'French (France)',
          isMain: false,
          isChosen: false
        }, {
          id: 'eng_GB',
          name: 'English (United Kingdom)',
          isMain: true,
          isChosen: true
        }])
        .then(res => expect(res).to.be.null);
    });
  });

  describe(`checkContent`, () => {
    it(`should check content for the chosen langauges`, () => {
      return api.checkContent([{
          id: 'unicore-cms-content-ffl-sn-prod',
          title: 'Facts For Life'
        }], [{
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
        .then(res => expect(res).to.be.null);
    });
  });

  describe(`serialize`, () => {
    describe(`url`, () => {
      it(`should parse urls`, () => {
        expect(serialize.url('https://www.a.com:3000/b/c?d=e&f=g#h/'))
        .to.deep.equal({
          error: null,
          value: {
            protocol: 'https',
            host: 'a.com',
            port: '3000',
            path: '/b/c'
          }
        });
      });

      it(`should support urls without protocols`, () => {
        expect(serialize.url('www.a.com'))
          .to.deep.equal({
            error: null,
            value: {
              protocol: 'http',
              host: 'a.com'
            }
          });
      });

      it(`should support urls without www's or protocols`, () => {
        expect(serialize.url('a.com'))
          .to.deep.equal({
            error: null,
            value: {
              protocol: 'http',
              host: 'a.com'
            }
          });
      });

      it(`should return an error for invalid urls`, () => {
        expect(serialize.url('a'))
          .to.deep.equal({
            error: {type: 'INVALID_URL'},
            value: null
          });
      });
    });
  });
});
