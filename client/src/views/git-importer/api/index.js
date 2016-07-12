import request from 'axios';
import constant from 'lodash/constant';
import * as endpoints from 'src/views/git-importer/api/endpoints';
import * as parse from 'src/views/git-importer/api/parse';
import * as serialize from 'src/views/git-importer/api/serialize';
import { catchResponse, catchResponseCode, throwResponse } from 'src/http';


const CODES = {
  PARSE_ERROR: 422
};


export function repos(url, opts) {
  return Promise.resolve(url)
    .then(serialize.url)
    .then(({error, value}) => !error
      ? reposGet(value, opts)
      : {
        error: error,
        value: null
      });
}


export function languages(repos, opts) {
  return request(endpoints.locales(repos.map(serialize.repoName), opts))
    .then(resp => resp.data.locales.map(parse.locale), catchResponse());
}


export function importContent(repos, languages, opts) {
  repos = repos.map(serialize.repo);
  languages = serialize.languages(languages);

  return request(endpoints.importContent(repos, languages, opts))
    .then(constant(null), catchResponse());
}


export function checkContent(repos, languages, opts) {
  repos = repos.map(serialize.repo);
  languages = serialize.languages(languages);
  return request(endpoints.validateContent(repos, languages, opts))
    .then(constant(null), catchResponse());
}


function reposGet(url, opts) {
  return request(endpoints.repos(url, opts))
    .then(
      reposGetSuccess,
      catchResponseCode(CODES.PARSE_ERROR, reposParseError));
}


function reposGetSuccess(resp) {
  return !resp.data.repos.length
    ? reposNoReposFound()
    : {
      error: null,
      value: resp.data.repos.map(parse.repo)
    };
}


function reposParseError(resp) {
  return resp.data.type !== 'site_response_error'
    ? throwResponse(resp)
    : reposNoReposFound();
}


function reposNoReposFound() {
  return {
    error: {type: 'NO_REPOS_FOUND'},
    value: null
  };
}
