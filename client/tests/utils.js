import dedent from 'dedent';
import constant from 'lodash/constant';
import identity from 'lodash/identity';


export function resolvesTo(v) {
  return constant(Promise.resolve(v));
}


export function doThunk(fn, ret=identity) {
  return fn(ret);
}


export function message(s, ...args) {
  return dedent(s, ...args).replace('\n', ' ');
}


export function captureDispatches(action) {
  let dispatches = [];
  return Promise.resolve(d => dispatches.push(d))
    .then(action)
    .then(resolvesTo(dispatches));
}
