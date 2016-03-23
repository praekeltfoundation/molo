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


export const validateContent = (id, locales, opts) => endpoint(opts, {
  method: 'POST',
  url: `/import/repos/${id}/validate/`,
  data: {locales},
  useAuth: true
});


function endpoint(opts, def) {
  return internalEndpoint(conj(def, opts || {}));
}
