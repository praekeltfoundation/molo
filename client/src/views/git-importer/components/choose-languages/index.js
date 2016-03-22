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

      <button
        type="button"
        className={importButtonClasses(d.status)}
        disabled={d.status === 'LOADING'}
        onClick={() => d.actions.importContent(d.site.id, d.languages)}>
        {importButtonText(d.status)}
      </button>
    </div>
  );


  function importButtonText(status) {
    return {
      IDLE: `Check content and import`,
      LOADING: `Checking and importing content...`,
      COMPLETE: `Import complete`
    }[status];
  }


  function importButtonClasses(status) {
    return status === 'COMPLETE'
      ? 'o-form-button o-form-button--success c-choose-languages__import'
      : 'o-form-button c-choose-languages__import';
  }


export default ChooseLanguages;
