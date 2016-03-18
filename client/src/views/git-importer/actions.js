import * as httpApi from 'src/views/git-importer/api';


export function expandStep(name) {
  return {
    type: 'EXPAND_STEP',
    payload: {name: name}
  };
}


export function updateSites(api=httpApi) {
  return dispatch => api.sites()
    .then(sites => ({
      type: 'UPDATE_SITES',
      payload: {sites: sites}
    }))
    .then(dispatch);
}


export function chooseSite(id, api=httpApi) {
  return dispatch => Promise.all([
    chooseSiteLoading(dispatch, id, api),
    chooseSiteDone(dispatch, id, api)
  ]);
}


function chooseSiteLoading(dispatch, id, api) {
  return Promise.resolve({
      type: 'CHOOSE_SITE/LOADING'
    })
    .then(dispatch);
}


function chooseSiteDone(dispatch, id, api) {
  return api.languages(id)
    .then(languages => ({
      type: 'CHOOSE_SITE/DONE',
      payload: {languages: languages}
    }))
    .then(dispatch);
}


export function chooseMain() {
  return {type: 'CHOOSE_MAIN'};
}


export function changeSite(id) {
  return {
    type: 'CHANGE_SITE',
    payload: {id: id}
  };
}


export function changeMain(id) {
  return {
    type: 'CHANGE_MAIN',
    payload: {id: id}
  };
}


export function toggleLanguageChosen(id) {
  return {
    type: 'TOGGLE_LANGUAGE_CHOSEN',
    payload: {id: id}
  };
}


export function importContent(id, languages, api=httpApi) {
  return dispatch => Promise.all([
    importContentLoading(dispatch, id, languages, api),
    importContentDone(dispatch, id, languages, api)
  ]);
}


function importContentLoading(dispatch, id, languages, api) {
  return Promise.resolve({
      type: 'IMPORT_CONTENT/LOADING'
    })
    .then(dispatch);
}


function importContentDone(dispatch, id, languages, api) {
  return api.importContent(id, languages)
    .then(d => ({
      type: 'IMPORT_CONTENT/DONE',
      payload: {errors: d.errors}
    }))
    .then(dispatch);
}
