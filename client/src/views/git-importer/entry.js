import React from 'react';
import { render } from 'react-dom';
import { Provider } from 'react-redux';
import configureStore from './store';
import GitImporterContainer from './containers/git-importer';
import { updateSites } from 'src/views/git-importer/actions';


let store = configureStore();
store.dispatch(updateSites());


render(
  <Provider store={store}>
    <GitImporterContainer/>
  </Provider>,
  document.getElementById('mountpoint')
);
