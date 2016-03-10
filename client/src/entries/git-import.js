import React from 'react';
import { render } from 'react-dom';
import { Provider } from 'react-redux';
import configureStore from '../stores/git-importer';
import GitImporter from '../components/git-importer';


render(
  <Provider store={configureStore()}>
    <GitImporter/>
  </Provider>,
  document.getElementById('root')
);
