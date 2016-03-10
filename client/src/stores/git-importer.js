import { createStore } from 'redux';
import reducer from '../reducers/git-importer.js';


const initialState = () => ({
  stub: 'TODO'
});


export default function configureStore() {
  return createStore(reducer, initialState());
}
