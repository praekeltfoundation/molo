import { createStore, applyMiddleware } from 'redux';
import reducer from './reducers';
import thunk from 'redux-thunk';


const initialState = () => ({
  ui: {
    state: 'IDLE',
    currentStep: 'site',
    lastStep: 'site'
  },
  data: {
    sites: [],
    site: null,
    languages: [],
    errors: []
  }
});


export default function configureStore() {
  return createStore(reducer, initialState(), applyMiddleware(thunk));
}
