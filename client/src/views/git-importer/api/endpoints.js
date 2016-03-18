import has from 'lodash/has';
import { conj } from 'src/utils';


export const repos = opts => endpoint(opts, {
  method: 'GET',
  url: '/import/repos/'
});


function endpoint(opts, def) {
  let d = conj(def, opts || {});
  if (has(d, 'prefix')) d.url = d.prefix + d.url;

  // request option parsing for all api endpoints goes here

  return d;
}
