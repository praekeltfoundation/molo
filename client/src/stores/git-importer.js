import { createStore } from 'redux';
import reducer from '../reducers/git-importer.js';

// TODO remove once we are hooked up to an api
import fixtures from '../../tests/fixtures/git-importer';


const initialState = () => fixtures('state');


export default function configureStore() {
  return createStore(reducer, initialState());
}
