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
        defaultChecked={language.isMain}
        onChange={() => d.actions.changeMain(language.id)} />
      <span>{language.name}</span>
    </li>
    )}
    </ul>

    <button type="button" onClick={d.actions.chooseMain}>
      Next
    </button>
  </div>
);


export default ChooseMain;
