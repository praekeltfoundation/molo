import React, { PropTypes } from 'react';


const GitImporter = (d) => (
  <form action="">
    <div className="c-importer">
      <ul className="fields">
        <li>
          <div className="import-step">
            <h2>Step 1: Fetch content from Github</h2>
            <input type="text" />

            <p className="add"><button>Fetch</button></p>
          </div>
        </li>

        <li>
          <div className="c-importer__step">
            <h2>Step 2: Choose which locales to import</h2>
            {/* TODO select all/none */}

            {d.locales.map(locale =>
              <div key={locale.name} className="input c-importer__locale">
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
