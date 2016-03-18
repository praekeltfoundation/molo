import { createStore } from 'redux';
import reducer from './reducers';

// TODO remove once we are hooked up to an api
import fixtures from 'tests/views/git-importer/fixtures';


const initialState = () => ({
  ui: {
    currentStep: 'site',
    lastStep: 'site'
  },
  data: {
    sites: fixtures('state').data.sites,
    site: null,
    languages: []
  }
});


export default function configureStore() {
  return createStore(reducer, initialState());
}
