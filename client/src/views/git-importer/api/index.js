import request from 'axios';
import constant from 'lodash/constant';
import * as endpoints from 'src/views/git-importer/api/endpoints';
import * as parse from 'src/views/git-importer/api/parse';
import * as serialize from 'src/views/git-importer/api/serialize';
import { catchResponse, catchResponseCode } from 'src/http';


const CODES = {
  VALIDATION_FAIL: 422
};


export function repos(url, opts) {
  return request(endpoints.repos(serialize.url(url), opts))
    .then(resp => resp.data.repos.map(parse.repo), catchResponse());
}


export function languages(repos, opts) {
  return request(endpoints.locales(repos.map(serialize.repoName), opts))
    .then(resp => resp.data.locales.map(parse.locale), catchResponse());
}


export function importContent(id, languages, opts) {
  return Promise.resolve(languages)
    .then(serialize.languages)
    .then(languages => endpoints.importContent(id, languages, opts))
    .then(request)
    .then(
      constant({
        errors: []
      }),
      catchResponseCode(CODES.VALIDATION_FAIL, resp => ({
        errors: resp.data.errors
      })));
}


export function checkContent(repos, languages, opts) {
  repos = repos.map(serialize.repo);
  languages = serialize.languages(languages);
  return request(endpoints.validateContent(repos, languages, opts))
    .then(resp => ({errors: resp.data.errors}), catchResponse());
}
