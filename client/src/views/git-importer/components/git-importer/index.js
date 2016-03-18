import React, { PropTypes } from 'react';
import Collapse from 'react-collapse';
import classNames from 'classnames';
import ChooseSite from 'src/views/git-importer/components/choose-site';
import ChooseMain from 'src/views/git-importer/components/choose-main';
import ChooseLanguages from 'src/views/git-importer/components/choose-languages';


const GitImporter = (d) => (
  <form action="">
    <div className="c-git-importer">
      <div className="o-collapse c-git-import-step c-git-import-step--site">
        <div
          className={stepHeaderClasses(d.steps.site)}
          disabled={d.steps.site.isDisabled}
          onClick={() => d.actions.expandStep('site')}>

          <h2 className="o-collapse-header__title">
            Step 1: Choose site to import from
          </h2>
        </div>

        <Collapse isOpened={d.steps.site.isExpanded}>
          <div className="o-collapse-body">
            <ChooseSite
              status={d.status}
              site={d.site}
              sites={d.sites}
              actions={d.actions} />
          </div>
        </Collapse>
      </div>

      <div className="o-collapse c-git-import-step c-git-import-step--main">
        <div
          className={stepHeaderClasses(d.steps.main)}
          disabled={d.steps.main.isDisabled}
          onClick={() => d.actions.expandStep('main')}>

          <h2 className="o-collapse-header__title">
            Step 2: Choose the main language
          </h2>
        </div>

        <Collapse isOpened={d.steps.main.isExpanded}>
          <div className="o-collapse-body">
            <ChooseMain languages={d.languages} actions={d.actions} />
          </div>
        </Collapse>
      </div>

      <div className="o-collapse c-git-import-step c-git-import-step--languages">
        <div
          className={stepHeaderClasses(d.steps.languages)}
          disabled={d.steps.languages.isDisabled}
          onClick={() => d.actions.expandStep('languages')}>

          <h2 className="o-collapse-header__title">
            Step 3: Choose which languages to import
          </h2>
        </div>

        <Collapse isOpened={d.steps.languages.isExpanded}>
          <div className="o-collapse-body">
            <ChooseLanguages
              status={d.status}
              site={d.site}
              languages={d.languages}
              actions={d.actions} />
          </div>
        </Collapse>
      </div>
    </div>
  </form>
);


function expandedClass(isExpanded) {
  return isExpanded
      ? 'o-collapse-header--is-expanded'
      : 'o-collapse-header--is-collapsed';
}


function stepHeaderClasses(step) {
  return classNames(
    'o-collapse-header',
    expandedClass(step.isExpanded));
}


GitImporter.propTypes = {
  languages: PropTypes.array.isRequired
};


export default GitImporter;
