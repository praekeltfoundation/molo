import React, { PropTypes } from 'react';
import Collapse from 'react-collapse';
import classNames from 'classnames';


const GitImporter = (d) => (
  <form action="">
    <div className="c-git-importer">
      <div className={stepClasses(d, 'fetch-content')}>
        <div className="o-collapse__header" href="">
          <h2 className="o-collapse__header-title">Step 1: Choose site to import from</h2>
        </div>

        <Collapse isOpened={stepIsExpanded(d, 'fetch-content')}>
          <div className="o-collapse__body">
            <p className="add"><button type="button" className="c-git-importer__fetch" onClick={d.actions.fetchContent}>Fetch</button></p>
          </div>
        </Collapse>
      </div>

      <div className={stepClasses(d, 'choose-locales')}>
        <div className="o-collapse__header" href="">
          <h2 className="o-collapse__header-title">Step 2: Choose which locales to import</h2>
        </div>

        <Collapse isOpened={stepIsExpanded(d, 'choose-locales')}>
          <div className="o-collapse__body">
            {/* TODO select all/none */}

            {d.locales.map(locale =>
              <div key={locale.name} className="input c-git-importer__locale">
                <input type="checkbox" />
                <span>{locale.name}</span>
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
  locales: PropTypes.array.isRequired
};


export default GitImporter;
