import extend from 'lodash/extend';


export function conj(...args) {
  return extend({}, ...args);
}
