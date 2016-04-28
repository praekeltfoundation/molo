import React from 'react';


const ChooseMain = (d) => (
  <div className="c-choose-main">
    <ul className="o-input-group">
    {d.languages.map(language =>
    <li
      key={language.id}
      className="o-input-group__item c-choose-main__language">
      <input
        type="radio"
        name="main-language"
        defaultChecked={language.isMain}
        onChange={() => d.actions.changeMain(language.id)} />
      <span className="o-input-group__label">{language.name}</span>
    </li>
    )}
    </ul>

    <button
      className="o-button"
      type="button"
      onClick={d.actions.chooseMain}>
      Next
    </button>
  </div>
);


export default ChooseMain;
