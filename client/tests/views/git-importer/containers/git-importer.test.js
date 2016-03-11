import React from 'react';
import { expect } from 'chai';
import fixtures from '../fixtures';
import { stateToProps } from 'views/git-importer/containers/git-importer';


describe(`GitImporterContainer`, () => {
  describe("stateToProps", () => {
    it("should map state to props", () => {
      expect(stateToProps(fixtures('state')))
        .to.deep.equal(fixtures('props'));
    });
  });
});
