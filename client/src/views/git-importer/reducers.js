import find from 'lodash/find';
import { conj, ensure } from 'src/utils';

// TODO remove once we are hooked up to an ap
import fixtures from 'tests/views/git-importer/fixtures';


export default function gitImporter(state, action) {
  switch (action.type) {
    case 'choose-site':
      return fixtures('state');
    case 'change-site':
      return conj(state, {
        data: conj(state.data, {
          site: ensure(find(state.data.sites, {id: action.id}), null)
        })
      });
    case 'expand-step':
      return conj(state, {
        ui: conj(state.ui, {
          currentStep: action.name
        })
      });
  }

  return state;
}
