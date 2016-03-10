import { createStore } from 'redux';
import reducer from '../reducers/git-importer.js';


const initialState = () => ({
  locales: []
});


export default function configureStore() {
  return createStore(reducer, initialState());
}
