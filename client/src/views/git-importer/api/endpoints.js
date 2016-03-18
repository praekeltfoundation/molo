import has from 'lodash/has';
import { conj } from 'src/utils';


export const repos = opts => endpoint(opts, {
  method: 'GET',
  url: '/import/repos/'
});


export const locales = (id, opts) => endpoint(opts, {
  method: 'GET',
  url: `/import/repos/${id}/`
});


function endpoint(opts, def) {
  let d = conj(def, opts || {});
  if (has(d, 'prefix')) d.url = d.prefix + d.url;

  // request option parsing relevant to all api endpoints goes here

  return d;
}
