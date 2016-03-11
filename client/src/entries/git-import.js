import React from 'react';
import { render } from 'react-dom';
import { Provider } from 'react-redux';
import configureStore from '../stores/git-importer';
import GitImporterContainer from '../containers/git-importer';


render(
  <Provider store={configureStore()}>
    <GitImporterContainer/>
  </Provider>,
  document.getElementById('mountpoint')
);
