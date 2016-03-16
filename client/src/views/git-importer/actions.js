export function chooseSite() {
  return {type: 'choose-site'};
}


export function changeSite(id) {
  return {
    type: 'change-site',
    id: id
  };
}
