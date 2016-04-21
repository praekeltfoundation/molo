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
  return request(endpoints.repos(serialize.url(url), opts))
    .then(resp => resp.data.repos.map(parse.repo), catchResponse());
}


export function languages(repos, opts) {
  return request(endpoints.locales(repos.map(serialize.repoName), opts))
    .then(resp => resp.data.locales.map(parse.locale), catchResponse());
}


export function importContent(repos, languages, opts) {
  repos = repos.map(serialize.repo);
  languages = serialize.languages(languages);

  return request(endpoints.importContent(repos, languages, opts))
    .then(
      constant({errors: []}),
      catchResponseCode(CODES.PARSE_ERROR, importContentParseError));
}


export function checkContent(repos, languages, opts) {
  repos = repos.map(serialize.repo);
  languages = serialize.languages(languages);
  return request(endpoints.validateContent(repos, languages, opts))
    .then(resp => ({errors: resp.data.errors}), catchResponse());
}


function importContentParseError(resp) {
  return resp.data.type === 'validation_failure'
    ? {errors: resp.data.errors}
    : throwResponse(resp);
}
