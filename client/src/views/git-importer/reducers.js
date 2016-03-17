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

    case 'UPDATE_SITES':
      return conj(state, {
        data: conj(state.data, {
          sites: action.payload.sites
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
      // HACK returning a new object here seems to cause react to render really
      // slowly here, so instead we mutate state. My guess is react is
      // performing many unnecessary re-renders for some reason.
      state.data = conj(state.data, {
        languages: state.data.languages
          .map(language => conj(language, {
            isMain: language.id === action.payload.id
          }))
      });

      return state;

    case 'TOGGLE_LANGUAGE_CHOSEN':
      // HACK same as for `change-main`
      state.data = conj(state.data, {
        languages: state.data.languages
          .map(language => conj(language, {
            isChosen: language.id === action.payload.id
              ? !language.isChosen
              : language.isChosen
          }))
      });

      return state;

    case 'IMPORT_CONTENT':
      // TODO
      return state;
  }

  return state;
}
