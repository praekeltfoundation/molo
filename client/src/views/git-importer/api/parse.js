export function repo(name) {
  return {
    id: name,
    name
  };
}


export function locale(d) {
  return {
    id: d.locale,
    name: d.name,

    // We receive this field as `is_main_language`, but since this field should
    // be set via the UI, it should always start off as `false`.
    isMain: false,

    isChosen: false
  };
}
