import React from 'react';
import ErrorItem from 'src/views/git-importer/components/error-item';


const ErrorList = (d) => (
  <div className="o-panel">
    <div className="o-panel-header o-panel-header--failure">
      <h2 className="o-panel-header__title">Errors found</h2>
    </div>

    <div className="o-panel-body o-list c-import-error-list">
      {d.errors.map((error, i) => (
        <ErrorItem key={i} error={error} />
      ))}
    </div>
  </div>
);


export default ErrorList;
