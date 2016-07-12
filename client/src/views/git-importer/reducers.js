import { conj } from 'src/utils';


export default function gitImporter(state, action) {
  switch (action.type) {
    case 'EXPAND_STEP':
      return conj(state, {
        ui: conj(state.ui, {
          currentStep: action.payload.name
        })
      });

    case 'CHOOSE_SITE/FETCHING_REPOS':
      return conj(state, {
        ui: conj(state.ui, {
          status: 'CHOOSE_SITE_FETCHING_REPOS'
        })
      });

    case 'CHOOSE_SITE/FETCHING_LANGUAGES':
      return conj(state, {
        ui: conj(state.ui, {
          status: 'CHOOSE_SITE_FETCHING_LANGUAGES'
        })
      });

    case 'CHOOSE_SITE/NO_REPOS_FOUND':
      return conj(state, {
        ui: conj(state.ui, {
          status: 'CHOOSE_SITE_NO_REPOS_FOUND'
        })
      });

    case 'CHOOSE_SITE/INVALID_URL':
      return conj(state, {
        ui: conj(state.ui, {
          status: 'CHOOSE_SITE_INVALID_URL'
        })
      });

    case 'CHOOSE_SITE/DONE':
      return conj(state, {
        ui: conj(state.ui, {
          status: 'IDLE',
          currentStep: 'main',
          lastStep: 'main'
        }),
        data: conj(state.data, {
          repos: action.payload.repos,
          languages: action.payload.languages
        })
      });

    case 'CHOOSE_MAIN':
      return conj(state, {
        ui: conj(state.ui, {
          currentStep: 'languages',
          lastStep: 'languages'
        }),
        data: conj(state.data, {
          languages: state.data.languages
            .map(language => conj(language, {
              isChosen: language.isMain
            }))
        })
      });

    case 'CHANGE_SITE_URL':
      return conj(state, {
        ui: conj(state.ui, {
          status: 'IDLE'
        }),
        data: conj(state.data, {
          siteUrl: action.payload.url
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

    case 'IMPORT_CONTENT/BUSY':
      return conj(state, {
        ui: conj(state.ui, {
          status: 'IMPORT_CONTENT_BUSY'
        })
      });

    case 'IMPORT_CONTENT/STARTED':
      return conj(state, {
        ui: conj(state.ui, {
          status: 'IMPORT_CONTENT_STARTED'
        })
      });

    case 'CHECK_CONTENT/BUSY':
      return conj(state, {
        ui: conj(state.ui, {
          status: 'CHECK_CONTENT_BUSY'
        })
      });

    case 'CHECK_CONTENT/STARTED':
      return conj(state, {
        ui: conj(state.ui, {
          status: 'CHECK_CONTENT_STARTED'
        })
      });
  }

  return state;
}
