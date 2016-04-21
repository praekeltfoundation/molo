import parseUrl from 'url-parse';
import normalizeUrl from 'normalize-url';
import omitBy from 'lodash/omitBy';
import isEmpty from 'lodash/isEmpty';


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

  return omitBy({
    protocol: parts.protocol.slice(0, -1),  // slice off ':' in 'http:'
    host: parts.hostname,
    port: parts.port,
    path: parts.pathname
  }, isEmpty);
}


function isChosen(d) {
  return d.isChosen;
}
