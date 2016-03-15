import React from 'react';


const ChooseSite = (d) => (
  <div>
    <p className="add"><button type="button" className="c-git-importer__choose-site" onClick={d.actions.fetchSite}>Next</button></p>
  </div>
);


export default ChooseSite;
