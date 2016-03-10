import React from 'react';


const GitImporter = (d) => (
  <form action="">
    <div className="c-git-importer">
      <ul className="fields">
        <li>
          <h2>Step 1: Fetch content from Github</h2>
          <input type="text" />

          <p className="add"><button>Fetch</button></p>
        </li>

        <li>
          <h2>Step 2: Choose which locales to import</h2>

          {/* TODO select all/none */}
          <div className="input">
            <input type="checkbox" />
            <span>en_ZA</span>
          </div>
        </li>

        <li>
          <button>Import</button>
        </li>
      </ul>
    </div>
  </form>
);


export default GitImporter;
