import constant from 'lodash/constant';
import identity from 'lodash/identity';


export function resolvesTo(v) {
  return constant(Promise.resolve(v));
}


export function thunk(fn) {
  return fn(identity);
}
