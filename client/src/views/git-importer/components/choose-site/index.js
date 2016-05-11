import React from 'react';
import includes from 'lodash/includes';
import { when } from 'src/utils';


const ChooseSite = (d) => (
  <div className="c-choose-site">
    <input
      type="text"
      name="site-url"
      className="c-choose-site__input"
      value={d.siteUrl}
      onChange={e => d.actions.changeSiteUrl(e.target.value)}
      placeholder="Enter a site to import (e.g. foo.bar.unicore.io)"
      autoFocus />

    {when(inputHasError(d.status), () => (
    <p className="c-choose-site__input-error error-message">
      <span>{getInputError(d.status)}</span>
    </p>
    ))}

    <button
      className="o-button c-choose-site__next"
      type="button"
      disabled={nextButtonIsDisabled(d.siteUrl, d.status)}
      onClick={() => d.actions.chooseSite(d.siteUrl)}>
      {nextButtonText(d.status)}
    </button>
  </div>
);


function inputHasError(status) {
  return includes([
    'CHOOSE_SITE_INVALID_URL',
    'CHOOSE_SITE_NO_REPOS_FOUND'
  ], status);
}


function getInputError(status) {
  switch (status) {
    case 'CHOOSE_SITE_INVALID_URL':
      return 'Please enter a valid url (e.g. foo.bar.unicore.io)';

    case 'CHOOSE_SITE_NO_REPOS_FOUND':
      return 'No content repositories were found for this site';
  }
}


function nextButtonText(status) {
  switch (status) {
    case 'CHOOSE_SITE_FETCHING_REPOS':
      return 'Fetching repos...';

    case 'CHOOSE_SITE_FETCHING_LANGUAGES':
      return 'Fetching languages...';

    default:
      return 'Next';
  }
}


function nextButtonIsDisabled(siteUrl, status) {
  return !siteUrl
      || includes([
          'CHOOSE_SITE_FETCHING_REPOS',
          'CHOOSE_SITE_FETCHING_LANGUAGES'
        ], status);
}


export default ChooseSite;
