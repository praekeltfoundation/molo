import { expect } from 'chai';
import fixtures from 'tests/views/git-importer/fixtures';
import { stateToProps } from 'src/views/git-importer/containers/git-importer';


describe(`GitImporterContainer`, () => {
  describe("stateToProps", () => {
    it("should map state to props", () => {
      expect(stateToProps(fixtures('state')))
        .to.deep.equal(fixtures('state-to-props'));
    });
  });
});
