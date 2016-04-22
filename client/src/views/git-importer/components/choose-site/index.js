import React from 'react';
import isNull from 'lodash/isNull';


const ChooseSite = (d) => (
  <div className="c-choose-site">
    <input
      type="text"
      className="c-choose-site__input"
      placeholder="Enter a site to import (e.g. foo.bar.unicore.io)"
      value={d.siteUrl}
      onChange={e => d.actions.changeSiteUrl(e.target.value)} />

    <button
      className="o-button c-choose-site__next"
      type="button"
      disabled={isNull(d.siteUrl) || d.status === 'CHOOSE_SITE_BUSY'}
      onClick={() => d.actions.chooseSite(d.siteUrl)}>
      {d.status === 'CHOOSE_SITE_BUSY'
        ? `Fetching languages...`
        : `Next`}
    </button>
  </div>
);


export default ChooseSite;
