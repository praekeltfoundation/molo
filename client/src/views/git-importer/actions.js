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


export function chooseSite() {
  return {type: 'CHOOSE_SITE'};
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


export function importContent() {
  return {type: 'IMPORT_CONTENT'};
}
