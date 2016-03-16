import find from 'lodash/find';
import { conj, ensure } from 'src/utils';

// TODO remove once we are hooked up to an api
import fixtures from 'tests/views/git-importer/fixtures';


export default function gitImporter(state, action) {
  switch (action.type) {
    case 'expand-step':
      return conj(state, {
        ui: conj(state.ui, {
          currentStep: action.name
        })
      });

    case 'choose-site':
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

    case 'choose-main':
      return conj(state, {
        ui: conj(state.ui, {
          currentStep: 'languages',
          lastStep: 'languages'
        })
      });

    case 'change-site':
      return conj(state, {
        data: conj(state.data, {
          site: ensure(find(state.data.sites, {id: action.id}), null)
        })
      });

    case 'change-main':
      // HACK returning a new object here seems to cause react to render really
      // slowly here, so instead we mutate state. My guess is react is
      // performing many unnecessary re-renders for some reason.
      state.data = conj(state.data, {
        languages: state.data.languages
          .map(language => conj(language, {
            isMain: language.id === action.id
          }))
      });

      return state;

    case 'toggle-language-chosen':
      // HACK same as for `change-main`
      state.data = conj(state.data, {
        languages: state.data.languages
          .map(language => conj(language, {
            isChosen: language.id === action.id
              ? !language.isChosen
              : language.isChosen
          }))
      });

      return state;

    case 'import-content':
      // TODO
      return state;
  }

  return state;
}
