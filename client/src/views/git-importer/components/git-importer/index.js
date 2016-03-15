import React, { PropTypes } from 'react';
import Collapse from 'react-collapse';
import classNames from 'classnames';


const GitImporter = (d) => (
  <form action="">
    <div className="c-git-importer">
      <div className={stepClasses(d, 'choose-site')}>
        <div className="o-collapse__header" href="">
          <h2 className="o-collapse__header-title">Step 1: Choose site to import from</h2>
        </div>

        <Collapse isOpened={stepIsExpanded(d, 'choose-site')}>
          <div className="o-collapse__body">
            <p className="add"><button type="button" className="c-git-importer__choose-site" onClick={d.actions.fetchSite}>Next</button></p>
          </div>
        </Collapse>
      </div>

      <div className={stepClasses(d, 'choose-main')}>
        <div className="o-collapse__header" href="">
          <h2 className="o-collapse__header-title">Step 2: Choose which locales to import</h2>
        </div>

        <Collapse isOpened={stepIsExpanded(d, 'choose-main')}>
          <div className="o-collapse__body">
            {/* TODO select all/none */}

            {d.languages.map(language =>
              <div key={language.name} className="input c-git-importer__language">
                <input type="checkbox" />
                <span>{language.name}</span>
              </div>
            )}

            <button type="button">Import</button>
          </div>
        </Collapse>
      </div>
    </div>
  </form>
);


function expandedClass(isExpanded) {
  return isExpanded
      ? 'is-expanded'
      : 'is-collapsed';
}


function stepClasses(d, stepName) {
  return classNames(
    'o-collapse',
    'c-git-import__step',
    expandedClass(stepIsExpanded(d, stepName)));
}


function stepIsExpanded(d, stepName) {
  return d.currentStep === stepName;
}


GitImporter.propTypes = {
  languages: PropTypes.array.isRequired
};


export default GitImporter;
