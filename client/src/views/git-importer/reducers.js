import { conj } from 'src/utils';

// TODO remove once we are hooked up to an api
import fixtures from 'tests/views/git-importer/fixtures';


export default function gitImporterReducer(state, action) {
  switch(state) {
    case 'fetch-content':
      return conj({
        locales: fixtures('state').locales
      });
  }
}
