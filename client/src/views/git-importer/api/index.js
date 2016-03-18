import request from 'axios';
import * as endpoints from 'src/views/git-importer/api/endpoints';
import * as parse from 'src/views/git-importer/api/parse';


export function sites(opts) {
  return request(endpoints.repos(opts))
    .then(resp => resp.data.repos.map(parse.repo));
}


export function languages(name, opts) {
  return request(endpoints.locales(name, opts))
    .then(resp => resp.data.locales.map(parse.locale));
}
