import React from 'react';
import { expect } from 'chai';
import { mount } from 'enzyme';
import { message } from 'tests/utils';
import ErrorMessage from 'src/views/git-importer/components/error-message';


function text(d) {
  const el = mount(<ErrorMessage {...d} />);
  return el.find('.c-import-error-message').text();
}


describe(`ErrorMessage`, () => {
  it(`should handle wrong_main_language_exist_in_wagtail`, () => {
    expect(text({
      type: 'wrong_main_language_exist_in_wagtail',
      details: {
        lang: 'French',
        selected_lang: 'Spanish (Mexico)'
      }
    }))
    .to.equal(message`
      The main language for the account is French, while the selected
      main language for this site is Spanish (Mexico)
    `);
  });

  it(`should handle no_primary_category`, () => {
    expect(text({
      type: 'no_primary_category',
      details: {
        lang: 'Spanish (Mexico)',
        article: 'Palabras sobre el embarazo y el parto'
      }
    }))
    .to.equal(message`
      No primary category found for page Palabras sobre el embarazo y el
      parto
    `);
  });

  it(`should handle no_source_found_for_category`, () => {
    expect(text({
      type: 'no_source_found_for_category',
      details: {
        category: 'La cabra siempre tira al monte',
        lang: 'Spanish (Mexico)'
      }
    }))
    .to.equal(message`
      No source found for category La cabra siempre tira al monte
    `);
  });

  it(`should handle no_source_found_for_page`, () => {
    expect(text({
      type: 'no_source_found_for_page',
      details: {
        article: 'La cabra siempre tira al monte',
        lang: 'Spanish (Mexico)'
      }
    }))
    .to.equal(message`
      No source found for page La cabra siempre tira al monte
    `);
  });

  it(`should handle category_source_not_exists`, () => {
    expect(text({
      type: 'category_source_not_exists',
      details: {
        category: 'La cabra siempre tira al monte',
        lang: 'Spanish (Mexico)'
      }
    }))
    .to.equal(message`
      The source for category La cabra siempre tira al monte does not exist
    `);
  });

  it(`should handle page_source_not_exists`, () => {
    expect(text({
      type: 'page_source_not_exists',
      details: {
        page: 'La cabra siempre tira al monte',
        lang: 'Spanish (Mexico)'
      }
    }))
    .to.equal(message`
      The source for page La cabra siempre tira al monte does not exist
    `);
  });
});
