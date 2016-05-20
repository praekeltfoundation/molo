import noop from 'lodash/noop';
import extend from 'lodash/extend';
import constant from 'lodash/constant';
import mapValues from 'lodash/mapValues';
import * as actions from 'src/views/git-importer/actions';
import { resolvesTo } from 'tests/utils';


function gitImporterFixtures(name) {
  switch (name) {
    case 'state':
      return {
        ui: {
          status: 'IDLE',
          currentStep: 'languages',
          lastStep: 'languages'
        },
        data: {
          siteUrl: 'foo.com',
          repos: [{
            id: 'foo-id',
            name: 'foo'
          }, {
            id: 'bar-id',
            name: 'bar'
          }],
          languages: [{
            id: 'en',
            name: 'English',
            isMain: true,
            isChosen: false
          }, {
            id: 'sw',
            name: 'Swahili',
            isMain: false,
            isChosen: true
          }],
          errors: []
        }
      };


    case 'state-to-props':
      return {
        status: 'IDLE',
        languages: [{
          id: 'en',
          name: 'English',
          isMain: true,
          isChosen: false
        }, {
          id: 'sw',
          name: 'Swahili',
          isMain: false,
          isChosen: true
        }],
        siteUrl: 'foo.com',
        repos: [{
          id: 'foo-id',
          name: 'foo'
        }, {
          id: 'bar-id',
          name: 'bar'
        }],
        steps: {
          site: {
            isDisabled: false,
            isExpanded: false
          },
          main: {
            isDisabled: false,
            isExpanded: false
          },
          languages: {
            isDisabled: false,
            isExpanded: true
          }
        },
        errors: []
      };


    case 'git-importer':
      return extend(gitImporterFixtures('state-to-props'), {
        actions: mapValues(actions, constant(noop))
      });


    case 'api':
      return {
        repos: resolvesTo([{
          id: 'foo-id',
          title: 'foo'
        }, {
          id: 'bar-id',
          title: 'bar'
        }]),
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
        }]),
        importContent: resolvesTo({
          errors: []
        })
      };
  }
}


export default gitImporterFixtures;
