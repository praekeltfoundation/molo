import { createStore } from 'redux';
import reducer from './reducers';


const initialState = () => ({
  site: null,
  languages: []
});


export default function configureStore() {
  return createStore(reducer, initialState());
}
