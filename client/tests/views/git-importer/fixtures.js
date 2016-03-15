import noop from 'lodash/noop';
import extend from 'lodash/extend';
import constant from 'lodash/constant';
import mapValues from 'lodash/mapValues';
import * as actions from 'src/views/git-importer/actions';


function gitImporterFixtures(name) {
  switch (name) {
    case 'state':
      return {
        locales: [{
          name: 'en_ZA'
        }, {
          name: 'zu_ZA'
        }]
      };
    case 'state-to-props:input':
      return gitImporterFixtures('state');
    case 'state-to-props:expected':
      return extend(gitImporterFixtures('state'), {
        currentStep: 'choose-locales'
      });
    case 'component:input':
      return extend(gitImporterFixtures('state'), {
        actions: mapValues(actions, constant(noop))
      });
  }
}


export default gitImporterFixtures;
