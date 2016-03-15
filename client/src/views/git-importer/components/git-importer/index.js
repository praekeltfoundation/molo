import React, { PropTypes } from 'react';
import Collapse from 'react-collapse';
import classNames from 'classnames';
import ChooseSite from 'src/views/git-importer/components/choose-site';
import ChooseMain from 'src/views/git-importer/components/choose-main';


const GitImporter = (d) => (
  <form action="">
    <div className="c-git-importer">
      <div className={stepClasses(d, 'choose-site')}>
        <div className="o-collapse__header" href="">
          <h2 className="o-collapse__header-title">Step 1: Choose site to import from</h2>
        </div>

        <Collapse isOpened={stepIsExpanded(d, 'choose-site')}>
          <div className="o-collapse__body">
            <ChooseSite actions={d.actions} />
          </div>
        </Collapse>
      </div>

      <div className={stepClasses(d, 'choose-main')}>
        <div className="o-collapse__header" href="">
          <h2 className="o-collapse__header-title">Step 2: Choose which locales to import</h2>
        </div>

        <Collapse isOpened={stepIsExpanded(d, 'choose-main')}>
          <div className="o-collapse__body">
            <ChooseMain languages={d.languages} actions={d.actions} />
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
