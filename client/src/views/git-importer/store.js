import { createStore } from 'redux';
import reducer from './reducers';


const initialState = () => ({
  ui: {
    currentStep: 'choose-site'
  },
  data: {
    sites: [],
    site: null,
    languages: []
  }
});


export default function configureStore() {
  return createStore(reducer, initialState());
}
