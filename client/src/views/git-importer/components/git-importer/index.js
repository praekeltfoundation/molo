import React, { PropTypes } from 'react';


const GitImporter = (d) => (
  <form action="">
    <div className="c-git-importer">
      <ul className="fields">
        <li>
          <div className="c-git-import__step">
            <h2>Step 1: Fetch content from Github</h2>
            <input type="text" />

            <p className="add"><button className="c-git-importer__fetch" onClick={d.actions.fetchContent}>Fetch</button></p>
          </div>
        </li>

        <li>
          <div className="c-git-importer__step">
            <h2>Step 2: Choose which locales to import</h2>
            {/* TODO select all/none */}

            {d.locales.map(locale =>
              <div key={locale.name} className="input c-git-importer__locale">
                <input type="checkbox" />
                <span>{locale.name}</span>
              </div>
            )}
          </div>
        </li>

        <li>
          <button>Import</button>
        </li>
      </ul>
    </div>
  </form>
);


GitImporter.propTypes = {
  locales: PropTypes.array.isRequired
};


export default GitImporter;
