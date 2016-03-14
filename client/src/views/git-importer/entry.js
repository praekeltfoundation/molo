import React from 'react';
import { render } from 'react-dom';
import { Provider } from 'react-redux';
import configureStore from './store';
import GitImporterContainer from './containers/git-importer';


let store = configureStore();


render(
  <Provider store={store}>
    <GitImporterContainer/>
  </Provider>,
  document.getElementById('mountpoint')
);
