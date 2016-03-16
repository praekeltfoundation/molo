import React from 'react';


const ChooseMain = (d) => (
  <div className="c-choose-main">
    <ul className="o-input-group">
    {d.languages.map(language =>
    <li
      key={language.name}
      className="o-input-group__item c-choose-main__language">
      <input
        type="radio"
        name="main-language"
        defaultChecked={language.isMain}
        onChange={() => d.actions.changeMain(language.id)} />
      <span>{language.name}</span>
    </li>
    )}
    </ul>

    <p className="add"><button type="button">Next</button></p>
  </div>
);


export default ChooseMain;
