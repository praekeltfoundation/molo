import find from 'lodash/find';
import { conj, ensure } from 'src/utils';


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

    case 'CHOOSE_SITE/LOADING':
      return conj(state, {
        ui: conj(state.ui, {
          isLoading: true
        })
      });

    case 'CHOOSE_SITE/DONE':
      return conj(state, {
        ui: conj(state.ui, {
          isLoading: false,
          currentStep: 'main',
          lastStep: 'main'
        }),
        data: conj(state.data, {
          languages: action.payload.languages
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

    case 'IMPORT_CONTENT/LOADING':
      return conj(state, {
        ui: conj(state.ui, {
          isLoading: true
        })
      });

    case 'IMPORT_CONTENT/DONE':
      return conj(state, {
        ui: conj(state.ui, {
          isLoading: false,
        }),
        data: conj(state.data, {
          errors: action.payload.errors
        })
      });
  }

  return state;
}
