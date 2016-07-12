import mapValues from 'lodash/mapValues';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import * as actions from 'src/views/git-importer/actions';
import GitImporter from 'src/views/git-importer/components/git-importer';
import { STEPS } from 'src/views/git-importer/consts';


function stateToProps(state) {
  return {
    status: state.ui.status,
    errors: state.data.errors,
    siteUrl: state.data.siteUrl,
    repos: state.data.repos,
    languages: state.data.languages,
    steps: mapValues(STEPS, (_, stepName) => ({
        isDisabled: stepIsDisabled(state, stepName),
        isExpanded: stepIsExpanded(state, stepName)
      })),
  };
}


function stepIsDisabled(state, stepName) {
  return STEPS[stepName] > STEPS[state.ui.lastStep];
}


function stepIsExpanded(state, stepName) {
  return state.ui.currentStep === stepName;
}


function dispatchToProps(dispatch) {
  return {
    actions: bindActionCreators(actions, dispatch)
  };
}


const GitImporterContainer = connect(
  stateToProps,
  dispatchToProps
)(GitImporter);


export { stateToProps };
export default GitImporterContainer;
