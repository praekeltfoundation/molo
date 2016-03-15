import React from 'react';


const ChooseMain = (d) => (
  <div>
    {/* TODO select all/none */}

    {d.languages.map(language =>
      <div key={language.name} className="input c-git-importer__language">
        <input type="checkbox" />
        <span>{language.name}</span>
      </div>
    )}

    <p className="add"><button type="button">Next</button></p>
  </div>
);


export default ChooseMain;
