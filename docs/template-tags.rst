.. _template-tags:

Template Tags
=============

Using template tags to get translations
---------------------------------------

In order to get the translation for a page model, we need to have the locale which is found in the context of a template.
This can be accessed from a template tag.

The following template tag will return the translation for the page model. It gets the locale from the context and returns the translation for that locale::

    get_translation(context, page)

Using template tags to render content
-------------------------------------

- The ``load_sections`` template tag returns all the sections for a specific page.
- The ``section_listing_homepage`` tag will return all the sections that are featured on the homepage.
- The ``latest_listing_homepage`` tag will return all the articles that have been promoted to feature on the homepage.
- The ``bannerpages`` tag will return all the bannerpages.
- The ``footer_page`` tag will return all the foooterpages.
- The ``breadcrumbs`` tag will return the current breadcrumbs.
- The ``load_descendant_articles_for_section`` tag will return all the articles that are children of a section or any of its child sections.
- The ``load_child_articles_for_section`` tag will return all the articled that are children of a section page.
- The ``load_child_sections_for_section`` tag will return all the sub-sections that are children of a section page.
