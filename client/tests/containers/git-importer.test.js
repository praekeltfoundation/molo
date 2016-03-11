import React from 'react';
import { expect } from 'chai';
import fixtures from '../fixtures/git-importer';
import { stateToProps } from '../../src/containers/git-importer';


describe(`GitImporterContainer`, () => {
  describe("stateToProps", () => {
    it("should map state to props", () => {
      expect(stateToProps(fixtures('state')))
        .to.deep.equal(fixtures('props'));
    });
  });
});
