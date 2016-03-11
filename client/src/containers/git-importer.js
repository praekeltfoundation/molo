import { connect } from 'react-redux';
import GitImporter from '../components/git-importer';


function stateToProps(state) {
  return {
    locales: state.locales
  };
}


const GitImporterContainer = connect(stateToProps)(GitImporter);


export { stateToProps };
export default GitImporterContainer;
