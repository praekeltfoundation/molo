import { createStore } from 'redux';
import reducer from './reducers';


const initialState = () => ({
  locales: []
});


export default function configureStore() {
  return createStore(reducer, initialState());
}
