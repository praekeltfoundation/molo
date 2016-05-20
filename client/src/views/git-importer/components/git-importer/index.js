import React, { PropTypes } from 'react';
import classNames from 'classnames';
import Collapse from 'src/components/collapse';
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
              siteUrl={d.siteUrl}
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
              repos={d.repos}
              languages={d.languages}
              actions={d.actions} />
          </div>
        </Collapse>
      </div>

      {statusInfo(d)}
    </div>
  </form>
);


function statusInfo(d) {
  switch (d.status) {
    case 'IMPORT_CONTENT_STARTED':
      return (
        <div className="c-git-import-status o-alert o-alert--success">
          Your import has been started. You will receive an email once the
          import is complete.
         </div>
      );

    case 'CHECK_CONTENT_STARTED':
      return (
        <div className="c-git-import-status o-alert o-alert--success">
          Error checking has been started. You will receive an email of the
          results once checking is complete.
        </div>
      );
  }
}


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
