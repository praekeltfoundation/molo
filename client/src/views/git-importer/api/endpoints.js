import { conj } from 'src/utils';
import { internalEndpoint } from 'src/http';


export const repos = opts => endpoint(opts, {
  method: 'GET',
  url: '/import/repos/'
});


export const locales = (id, opts) => endpoint(opts, {
  method: 'GET',
  url: `/import/repos/${id}/`
});


export const importContent = (id, locales, opts) => endpoint(opts, {
  method: 'POST',
  url: `/import/repos/${id}/import/`,
  data: {locales},
  useAuth: true
});


function endpoint(opts, def) {
  let d = conj(def, opts || {});
  // request option parsing relevant to all api endpoints goes here
  return internalEndpoint(d);
}
