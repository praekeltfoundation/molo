import noop from 'lodash/noop';
import extend from 'lodash/extend';
import constant from 'lodash/constant';
import mapValues from 'lodash/mapValues';
import * as actions from 'src/views/git-importer/actions';


function gitImporterFixtures(name) {
  switch (name) {
    case 'state':
      return {
        ui: {
          currentStep: 'choose-main'
        },
        data: {
          sites: [{
            id: 'foo-id',
            name: 'foo'
          }, {
            id: 'bar-id',
            name: 'bar'
          }],
          site: {
            id: 'foo-id',
            name: 'foo'
          },
          languages: [{
            id: 'en',
            name: 'English'
          }, {
            id: 'sw',
            name: 'Swahili'
          }]
        }
      };
    case 'state-to-props':
      return {
        currentStep: 'choose-main',
        languages: [{
          id: 'en',
          name: 'English'
        }, {
          id: 'sw',
          name: 'Swahili'
        }],
        site: {
          id: 'foo-id',
          name: 'foo'
        },
        sites: [{
          id: 'foo-id',
          name: 'foo'
        }, {
          id: 'bar-id',
          name: 'bar'
        }]
      };
    case 'git-importer':
      return extend(gitImporterFixtures('state-to-props'), {
        actions: mapValues(actions, constant(noop))
      });
  }
}


export default gitImporterFixtures;
