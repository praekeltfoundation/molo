// TODO remove once we are hooked up to an api
import fixtures from 'tests/views/git-importer/fixtures';


export default function gitImporterReducer(state, action) {
  switch (action.type) {
    case 'fetch-site':
      return fixtures('state');
  }

  return state;
}
