import React from 'react';


const ErrorMessage = d => {
  switch (d.type) {
    case 'wrong_main_language_exist_in_wagtail':
      return (
        <p className="c-import-error-message">
        The main language for the account is <strong>{d.details.lang}</strong>,
         while the selected main language for this site is <strong>{d.details.selected_lang}</strong>
        </p>
      );

    case 'no_primary_category':
      return (
        <p className="c-import-error-message">
          No primary category found for page <strong>{d.details.article}</strong>
        </p>
      );

    case 'no_source_found_for_category':
      return (
        <p className="c-import-error-message">
          No source found for category <strong>{d.details.category}</strong>
        </p>
      );

    case 'no_source_found_for_page':
      return (
        <p className="c-import-error-message">
          No source found for page <strong>{d.details.article}</strong>
        </p>
      );

    case 'category_source_not_exists':
      return (
        <p className="c-import-error-message">
          The source for category <strong>{d.details.category}</strong> does not exist
        </p>
      );

    case 'page_source_not_exists':
      return (
        <p className="c-import-error-message">
          The source for page <strong>{d.details.page}</strong> does not exist
        </p>
      );
  }
};


export default ErrorMessage;
