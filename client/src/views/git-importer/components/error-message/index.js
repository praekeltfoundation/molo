import React from 'react';


const ErrorMessage = d => {
  switch (d.type) {
    case 'wrong_main_language_exist_in_wagtail':
      return (
        <div className="c-import-error-message">
        The main language for the account is <span className="o-text--info">{d.details.lang}</span>, while the selected main language for this site is <span className="o-text--info">{d.details.selected_lang}</span>
        </div>
      );

    case 'no_primary_category':
      return (
        <div className="c-import-error-message">
          <span className="o-text--primary o-text--label">{d.details.lang}</span> No primary category found for page <span className="o-text--info">{d.details.article}</span>
        </div>
      );

    case 'no_source_found_for_category':
      return (
        <div className="c-import-error-message">
          <span className="o-text--primary o-text--label">{d.details.lang}</span> No source found for category <span className="o-text--info">{d.details.category}</span>
        </div>
      );

    case 'no_source_found_for_page':
      return (
        <div className="c-import-error-message">
          <span className="o-text--primary o-text--label">{d.details.lang}</span> No source found for page <span className="o-text--info">{d.details.article}</span>
        </div>
      );

    case 'category_source_not_exists':
      return (
        <div className="c-import-error-message">
          <span className="o-text--primary o-text--label">{d.details.lang}</span> The source for category <span className="o-text--info">{d.details.category}</span> does not exist
        </div>
      );

    case 'page_source_not_exists':
      return (
        <div className="c-import-error-message">
          <span className="o-text--primary o-text--label">{d.details.lang}</span> The source for page <span className="o-text--info">{d.details.page}</span> does not exist
        </div>
      );
  }
};


export default ErrorMessage;
