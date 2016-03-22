import { message } from 'src/utils';


export function parse(d) {
  switch (d.type) {
    case 'wrong_main_language_exist_in_wagtail':
      return message`
        The main language for this account is ${d.details.lang}, while the
        selected main language for this site is ${d.details.selected_lang}
      `;

    case 'no_primary_category':
      return message`
        No primary category found for page '${d.details.article}'
      `;

    case 'no_source_found_for_category':
      return message`
        No source found for category '${d.details.category}'
      `;

    case 'no_source_found_for_page':
      return message`
        No source found for page '${d.details.article}'
      `;

    case 'category_source_not_exists':
      return message`
        The source for category '${d.details.category}' does not exist
      `;

    case 'page_source_not_exists':
      return message`
        The source for page '${d.details.page}' does not exist
      `;
  }
}
