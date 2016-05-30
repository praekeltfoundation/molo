import * as httpApi from 'src/views/git-importer/api';


export function expandStep(name) {
  return {
    type: 'EXPAND_STEP',
    payload: {name}
  };
}


export function changeSiteUrl(url) {
  return {
    type: 'CHANGE_SITE_URL',
    payload: {url}
  };
}


export function chooseSite(url, api=httpApi) {
  // TODO handle site not found
  return dispatch => Promise.resolve()
    .then(() => chooseSiteFetchingRepos())
    .then(dispatch)
    .then(() => api.repos(url))
    .then(({error, value}) => error
      ? chooseSiteHandleError(dispatch, error, api)
      : chooseSiteHandleSuccess(dispatch, value, api));
}


function chooseSiteHandleError(dispatch, error, api) {
  return Promise.resolve()
    .then(() => chooseSiteError(error))
    .then(dispatch);
}


function chooseSiteHandleSuccess(dispatch, repos, api) {
  return Promise.resolve()
    .then(() => chooseSiteFetchingLanguages())
    .then(dispatch)
    .then(() => Promise.all([repos, api.languages(repos)]))
    .then(([repos, languages]) => chooseSiteDone(repos, languages))
    .then(dispatch);
}


function chooseSiteError(error) {
  switch (error.type) {
    case 'INVALID_URL':
      return {type: 'CHOOSE_SITE/INVALID_URL'};

    case 'NO_REPOS_FOUND':
      return {type: 'CHOOSE_SITE/NO_REPOS_FOUND'};
  }
}


function chooseSiteFetchingRepos() {
  return {type: 'CHOOSE_SITE/FETCHING_REPOS'};
}


function chooseSiteFetchingLanguages() {
  return {type: 'CHOOSE_SITE/FETCHING_LANGUAGES'};
}


function chooseSiteDone(repos, languages) {
  return {
    type: 'CHOOSE_SITE/DONE',
    payload: {
      repos,
      languages
    }
  };
}


export function chooseMain() {
  return {type: 'CHOOSE_MAIN'};
}


export function changeMain(id) {
  return {
    type: 'CHANGE_MAIN',
    payload: {id}
  };
}


export function toggleLanguageChosen(id) {
  return {
    type: 'TOGGLE_LANGUAGE_CHOSEN',
    payload: {id}
  };
}


export function importContent(repos, languages, api=httpApi) {
  return dispatch => Promise.resolve()
    .then(() => importContentBusy())
    .then(dispatch)
    .then(() => api.importContent(repos, languages))
    .then(() => importContentStarted())
    .then(dispatch);
}


function importContentBusy() {
  return {type: 'IMPORT_CONTENT/BUSY'};
}


function importContentStarted() {
  return {
    type: 'IMPORT_CONTENT/STARTED',
  };
}


export function checkContent(repos, languages, api=httpApi) {
  return dispatch => Promise.resolve()
    .then(() => checkContentBusy())
    .then(dispatch)
    .then(() => api.checkContent(repos, languages))
    .then(() => checkContentStarted())
    .then(dispatch);
}


function checkContentBusy() {
  return {type: 'CHECK_CONTENT/BUSY'};
}


function checkContentStarted() {
  return {
    type: 'CHECK_CONTENT/STARTED'
  };
}
