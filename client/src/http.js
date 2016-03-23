import isNull from 'lodash/isNull';
import defaults from 'lodash/defaults';
import conf from 'src/conf';


export function internalEndpoint(def) {
  let d = defaults({}, def, {headers: {}});
  defaults(d.headers, conf.apiHeaders);

  if (d.useAuth && !isNull(conf.csrfToken))
    d.headers['X-CSRFToken'] = conf.csrfToken;

  d.url = conf.apiPrefix + d.url;
  return d;
}


export function catchResponse(fn=throwResponse) {
  return obj => {
    if (obj instanceof Error) throw obj;
    return fn(obj);
  };
}


export function catchResponseCode(code, fn) {
  return catchResponse(resp => {
    if (resp.status === code) return fn(resp);
    else throwResponse(resp);
  });
}


export function throwResponse(resp) {
  throw new ResponseError(resp.toString());
}


class ResponseError extends Error {}
