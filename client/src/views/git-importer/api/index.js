import request from 'axios';
import constant from 'lodash/constant';
import * as endpoints from 'src/views/git-importer/api/endpoints';
import * as parse from 'src/views/git-importer/api/parse';
import * as serialize from 'src/views/git-importer/api/serialize';
import { responseErrback } from 'src/http';


export function sites(opts) {
  return request(endpoints.repos(opts))
    .then(resp => resp.data.repos.map(parse.repo), responseErrback());
}


export function languages(id, opts) {
  return request(endpoints.locales(id, opts))
    .then(resp => resp.data.locales.map(parse.locale), responseErrback());
}


export function importContent(id, languages, opts) {
  return Promise.resolve(languages)
    .then(serialize.languages)
    .then(languages => endpoints.importContent(id, languages, opts))
    .then(request)
    .then(
      constant({errors: []}),
      responseErrback(d => d.data.errors));
}
