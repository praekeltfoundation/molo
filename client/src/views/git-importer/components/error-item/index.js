import React from 'react';
import ErrorMessage from 'src/views/git-importer/components/error-message';


const ErrorItem = (d) => (
  <div class="c-import-error-item">
    <ErrorMessage {...d.error} />
  </div>
);


export default ErrorItem;
