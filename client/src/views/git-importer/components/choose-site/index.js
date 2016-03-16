import React from 'react';
import isNull from 'lodash/isNull';
import { Typeahead as Search } from 'react-typeahead';


const ChooseSite = (d) => (
  <div className="c-choose-site">
    {/* TODO handle keyups */}
    <Search
      placeholder="Enter a site to search for (e.g. unicore-cms-content-site)"
      value={displaySite(d.site)}
      options={d.sites}
      maxVisible={10}
      filterOption="name"
      displayOption={displaySite}
      className="c-choose-site__search"
      customClasses={{
        input: 'o-search__input',
        results: 'o-search__results',
        listItem: 'o-search__item',
        listAnchor: 'o-search__anchor',
        typeahead: 'o-serach__typeahead'
      }}
      onOptionSelected={site => d.actions.changeSite(site.id)} />

    <button
      className="o-form-button c-choose-site__next"
      type="button"
      disabled={isNull(d.site)}
      onClick={d.actions.chooseSite}>
      Next
    </button>
  </div>
);


function displaySite(site) {
  return !isNull(site)
    ? site.name
    : null;
}


export default ChooseSite;
