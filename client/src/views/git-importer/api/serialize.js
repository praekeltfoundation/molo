export function languages(data) {
  return data
    .filter(isChosen)
    .map(language);
}


export function language(d) {
  return {
    locale: d.id,
    is_main: d.isMain
  };
}


function isChosen(d) {
  return d.isChosen;
}
