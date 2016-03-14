import React, { PropTypes } from 'react';
import Collapse from 'react-collapse';


const GitImporter = (d) => (
  <form action="">
    <div className="c-git-importer">
      <div className="c-git-import__step">
        <h2>Step 1: Choose site to import from</h2>

        <Collapse isOpened={true}>
          <div>
            <p className="add"><button type="button" className="c-git-importer__fetch" onClick={d.actions.fetchContent}>Fetch</button></p>
          </div>
        </Collapse>
      </div>

      <div className="c-git-import__step">
        <h2>Step 2: Choose which locales to import</h2>

        <Collapse isOpened={d.locales.length > 0}>
          <div>
            {/* TODO select all/none */}

            {d.locales.map(locale =>
              <div key={locale.name} className="input c-git-importer__locale">
                <input type="checkbox" />
                <span>{locale.name}</span>
              </div>
            )}

            <button type="button">Import</button>
          </div>
        </Collapse>
      </div>
    </div>
  </form>
);


GitImporter.propTypes = {
  locales: PropTypes.array.isRequired
};


export default GitImporter;
