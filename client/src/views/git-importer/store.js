import { createStore } from 'redux';
import reducer from './reducers';

// TODO remove once we are hooked up to an api
import fixtures from '../../../tests/views/git-importer/fixtures';


const initialState = () => fixtures('state');


export default function configureStore() {
  return createStore(reducer, initialState());
}
