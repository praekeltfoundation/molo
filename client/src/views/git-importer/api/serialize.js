import parseUrl from 'url-parse';
import normalizeUrl from 'normalize-url';
import omitBy from 'lodash/omitBy';
import isEmpty from 'lodash/isEmpty';


export function repoName(d) {
  return d.id;
}


export function repo(d) {
  return {
    name: d.id,
    title: d.title
  };
}


export function languages(data) {
  return data
    .filter(isChosen)
    .map(language);
}


export function language(d) {
  return {
    locale: d.id,
    is_main: d.isMain
  };
}


export function url(rawUrl) {
  let parts = parseUrl(normalizeUrl(rawUrl));

  return !urlIsValid(parts)
    ? {
      error: {type: 'INVALID_URL'},
      value: null
    }
    : {
      error: null,
      value: omitBy({
        protocol: parts.protocol.slice(0, -1),  // slice off ':' in 'http:'
        host: parts.hostname,
        port: parts.port,
        path: parts.pathname
      }, isEmpty)
    };
}


function urlIsValid(parts) {
  return parts.host
      && parts.host.includes('.');
}


function isChosen(d) {
  return d.isChosen;
}
