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
          currentStep: 'main',
          lastStep: 'main'
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
            name: 'English',
            isMain: true
          }, {
            id: 'sw',
            name: 'Swahili',
            isMain: false
          }]
        }
      };

    case 'state-to-props':
      return {
        languages: [{
          id: 'en',
          name: 'English',
          isMain: true
        }, {
          id: 'sw',
          name: 'Swahili',
          isMain: false
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
        }],
        steps: {
          main: {
            isDisabled: false,
            isExpanded: true
          },
          site: {
            isDisabled: false,
            isExpanded: false
          }
        }
      };

    case 'git-importer':
      return extend(gitImporterFixtures('state-to-props'), {
        actions: mapValues(actions, constant(noop))
      });
  }
}


export default gitImporterFixtures;
