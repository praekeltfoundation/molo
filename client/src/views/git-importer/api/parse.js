export function repo(name) {
  return {
    id: name,
    name
  };
}


export function locale(d, i) {
  return {
    id: d.locale,
    name: d.name,

    // We receive this field as `is_main_language`, but since this field should
    // be set via the UI, we initialise it ourselves. We set the first locale
    // to `true` to provide a default, and set the rest of the locales to
    // `false`.
    isMain: i < 1,
    isChosen: i < 1
  };
}
