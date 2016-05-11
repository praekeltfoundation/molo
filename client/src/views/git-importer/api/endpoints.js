import { conj } from 'src/utils';
import { internalEndpoint } from 'src/http';


export const repos = (urlParts, opts) => endpoint(opts, {
  method: 'GET',
  url: '/import/repos/',
  params: urlParts
});


export const locales = (repoNames, opts) => endpoint(opts, {
  method: 'GET',
  url: `/import/languages/`,
  params: {repo: repoNames}
});


export const importContent = (repos, locales, opts) => endpoint(opts, {
  method: 'PUT',
  url: `/import/content/`,
  data: {
    repos,
    locales
  },
  useAuth: true
});


export const validateContent = (repos, locales, opts) => endpoint(opts, {
  method: 'POST',
  url: '/import/validation/',
  data: {
    repos,
    locales
  },
  useAuth: true
});


function endpoint(opts, def) {
  return internalEndpoint(conj(def, opts || {}));
}
