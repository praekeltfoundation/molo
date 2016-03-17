import find from 'lodash/find';
import { conj, ensure } from 'src/utils';

// TODO remove once we are hooked up to an api
import fixtures from 'tests/views/git-importer/fixtures';


export default function gitImporter(state, action) {
  switch (action.type) {
    case 'EXPAND_STEP':
      return conj(state, {
        ui: conj(state.ui, {
          currentStep: action.payload.name
        })
      });

    case 'CHOOSE_SITE':
      // TODO get languages from api
      return conj(state, {
        data: conj(state.data, {
          languages: fixtures('state').data.languages
        }),
        ui: conj(state.ui, {
          currentStep: 'main',
          lastStep: 'main'
        })
      });

    case 'CHOOSE_MAIN':
      return conj(state, {
        ui: conj(state.ui, {
          currentStep: 'languages',
          lastStep: 'languages'
        })
      });

    case 'CHANGE_SITE':
      return conj(state, {
        data: conj(state.data, {
          site: ensure(find(state.data.sites, {id: action.payload.id}), null)
        })
      });

    case 'CHANGE_MAIN':
      return conj(state, {
        data: conj(state.data, {
          languages: state.data.languages
            .map(language => conj(language, {
              isMain: language.id === action.payload.id
          }))
        })
      });

    case 'TOGGLE_LANGUAGE_CHOSEN':
      return conj(state, {
        data: conj(state.data, {
          languages: state.data.languages
            .map(language => conj(language, {
              isChosen: language.id === action.payload.id
                ? !language.isChosen
                : language.isChosen
          }))
        })
      });

    case 'IMPORT_CONTENT':
      // TODO
      return state;
  }

  return state;
}
