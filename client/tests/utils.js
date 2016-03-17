import constant from 'lodash/constant';


export function resolvesTo(v) {
  return constant(Promise.resolve(v));
}
