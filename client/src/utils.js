import dedent from 'dedent';
import extend from 'lodash/extend';
import isUndefined from 'lodash/isUndefined';


export function conj(...args) {
  return extend({}, ...args);
}


export function ensure(v, defaultVal) {
  return isUndefined(v)
    ? defaultVal
    : v;
}


export function message(s, ...args) {
  return dedent(s, ...args).replace('\n', ' ');
}
