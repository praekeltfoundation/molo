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


export function when(truth, fn) {
  return truth
    ? fn()
    : void 0;
}
