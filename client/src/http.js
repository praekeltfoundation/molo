import isNull from 'lodash/isNull';
import defaults from 'lodash/defaults';
import conf from 'src/conf';


export function internalEndpoint(def) {
  let d = defaults({}, def, {headers: {}});

  if (d.useAuth && !isNull(conf.csrfToken))
    d.headers['X-CSRFToken'] = conf.csrfToken;

  d.url = conf.apiPrefix + d.url;
  return d;
}
