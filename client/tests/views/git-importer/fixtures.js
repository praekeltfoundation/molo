import noop from 'lodash/noop';
import extend from 'lodash/extend';
import constant from 'lodash/constant';
import mapValues from 'lodash/mapValues';
import * as actions from 'src/views/git-importer/actions';


function gitImporterFixtures(name) {
  switch (name) {
    case 'state':
      return gitImporterFixtures('state:choose-main');
    case 'state:choose-main':
      return {
        ui: {
          currentStep: 'choose-main'
        },
        data: {
          sites: [{
            name: 'foo'
          }, {
            name: 'bar'
          }],
          site: {
            name: 'foo'
          },
          languages: [{
            name: 'English'
          }, {
            name: 'Swahili'
          }]
        }
      };
    case 'state-to-props:input':
      return gitImporterFixtures('state');
    case 'state-to-props:expected':
      return {
        currentStep: 'choose-main',
        languages: [{
          name: 'English'
        }, {
          name: 'Swahili'
        }]
      };
    case 'component:input':
      return extend(gitImporterFixtures('state-to-props:expected'), {
        actions: mapValues(actions, constant(noop))
      });
  }
}


export default gitImporterFixtures;
