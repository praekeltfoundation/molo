import * as httpApi from 'src/views/git-importer/api';


export function expandStep(name) {
  return {
    type: 'EXPAND_STEP',
    payload: {name: name}
  };
}


export function chooseSite(url, api=httpApi) {
  // TODO handle site not found
  return dispatch => Promise.resolve()
    .then(() => chooseSiteBusy())
    .then(dispatch)
    .then(() => api.repos(url))
    .then(repos => Promise.all([repos, api.languages(repos)]))
    .then(([repos, languages]) => chooseSiteDone(repos, languages))
    .then(dispatch);
}


function chooseSiteBusy() {
  return {type: 'CHOOSE_SITE/BUSY'};
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
  return dispatch => Promise.resolve()
    .then(() => importContentBusy())
    .then(dispatch)
    .then(() => api.importContent(id, languages))
    .then(d => importContentDone(d))
    .then(dispatch);
}


function importContentBusy() {
  return {type: 'IMPORT_CONTENT/BUSY'};
}


function importContentDone(d) {
  return {
    type: 'IMPORT_CONTENT/DONE',
    payload: {errors: d.errors}
  };
}


export function checkContent(id, languages, api=httpApi) {
  return dispatch => Promise.resolve()
    .then(() => checkContentBusy())
    .then(dispatch)
    .then(() => api.checkContent(id, languages))
    .then(d => checkContentDone(d))
    .then(dispatch);
}


function checkContentBusy() {
  return {type: 'CHECK_CONTENT/BUSY'};
}


function checkContentDone(d) {
  return {
    type: 'CHECK_CONTENT/DONE',
    payload: {errors: d.errors}
  };
}
