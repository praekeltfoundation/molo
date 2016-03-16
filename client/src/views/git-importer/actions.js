export function expandStep(name) {
  return {
    type: 'expand-step',
    name: name
  };
}


export function chooseSite() {
  return {type: 'choose-site'};
}


export function changeSite(id) {
  return {
    type: 'change-site',
    id: id
  };
}


export function changeMain(id) {
  return {
    type: 'change-main',
    id: id
  };
}
