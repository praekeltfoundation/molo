import React from 'react';


const ChooseLanguages = (d) => (
  <div className="c-choose-languages">
    <ul className="o-input-group">
    {d.languages.map(language =>
    <li
      key={language.name}
      className="o-input-group__item c-choose-languages__language">
      {/* TODO make it clear that main language is always checked */}
      <input
        type="checkbox"
        disabled={language.isMain}
        defaultChecked={language.isMain}
        onChange={() => d.actions.toggleLanguageChosen(language.id)} />
      <span className="o-input-group__label">{language.name}</span>
    </li>
    )}
    </ul>

    <button className="o-form-button" type="button" onClick={d.actions.importContent}>
      Import
    </button>
  </div>
);


export default ChooseLanguages;
