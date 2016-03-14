import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import * as actions from 'src/views/git-importer/actions';
import GitImporter from 'src/views/git-importer/components/git-importer';


function stateToProps(state) {
  return {
    locales: state.locales
  };
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
