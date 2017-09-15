Template Tags
=============

Using template tags to get translations
---------------------------------------

In order to get the translation for a page model, we need to have the locale which is found in the context of a template.
This can be accessed from a template tag.

``get_translation``
~~~~~~~~~~~~~~~~~~~

Returns the translation for the page model. It gets the locale from the context and returns the translation for that locale::

    get_translation(context, page)

``get_pages``
~~~~~~~~~~~~~

Takes in context, a queryset and a locale. It returns all the pages in their correct locale::

    get_pages(context, qs, locale)

``render_translations``
~~~~~~~~~~~~~~~~~~~~~~~

Takes in context and a page. It renders the translated pages in wagtail CMS::

    render_translations(context, page)

Using template tags to render content
-------------------------------------

Content for Home Page
~~~~~~~~~~~~~~~~~~~~~
The ``section_listing_homepage`` tag will return all the sections with articles in them that are featured on the homepage::

    section_listing_homepage(context)

The ``latest_listing_homepage`` tag will return all the articles that are featured in latest section on the homepage::

    latest_listing_homepage(context)

The ``bannerpages`` tag will return all the banners that are live::

    bannerpages(context)

The ``footer_page`` tag will return all the footer pages that are live::

    footer_page(context)

``social_media_footer``
~~~~~~~~~~~~~~~~~~~~~~~

Returns the social media footer::

  social_media_footer(context)

The ``tag_menu_homepage`` tag will return all the tags that are live::

  tag_menu_homepage(context)

The ``topic_of_the_day`` tag will return the article that has been promoted as the topic of the day::

  topic_of_the_day(context)

The ``get_tag_articles`` tag is a bit more complex. It returns all the content you can have on your homepage.
It takes in a ``section_count``. This is the amount of section you want appearing on your homepage. It takes in a ``tag_count``.
This is the amount of articles you want appearing under each tag that has been promoted to the homepage.
It takes in a ``sec_articles_count``. This is the amount of articles you want appearing under each section, as well
as a latest article count. This is the amount of articles featured in latest that will have preference in placement.
This will return all the content rendered on the homepage, excluding banners and footers. It is done in such a way that no
articles on the homepage are repeated::

    get_tag_articles(
            context, section_count=1, tag_count=4, sec_articles_count=4,
            latest_article_count=3)


Content for Section Pages
~~~~~~~~~~~~~~~~~~~~~~~~~

``get_tags_for_section``
~~~~~~~~~~~~~~~~~~~~~~~~

Returns the tags that are shown in a section (amount specified by ``tag_count``)
with the articles for that tag (amount specific by ``tag_article_count``)::

  get_tags_for_section(context, section, tag_count=2, tag_article_count=4)

``load_sections``
~~~~~~~~~~~~~~~~~

Returns all the section that are live for a specific Main page::

  load_sections(context)

``breadcrumbs``
~~~~~~~~~~~~~~~

Returns the breadcrumb for the current page if the current page is not the homepage::

  breadcrumbs(context)

``load_child_articles_for_section``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Returns articles that are children of a specific section page (amount specified by ``count``)::

  load_child_articles_for_section(context, section, count=5)

``load_descendant_articles_for_section``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Returns articles that are descendants of a specific section page (amount specified by ``count``).
It is possible to specify whether these articles have to be featured in the homepage, section or latest::

  load_descendant_articles_for_section(
          context, section, featured_in_homepage=None, featured_in_section=None,
          featured_in_latest=None, count=5)

``load_child_sections_for_section``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Returns all the child sections for a specific question. The amount returned can be limited by count::

  load_child_sections_for_section(context, section, count=None)

Content for Articles Pages
~~~~~~~~~~~~~~~~~~~~~~~~~~

``get_parent``
~~~~~~~~~~~~~~

Returns the parent page of an article page::

  get_parent(context, page)

``get_next_article``
~~~~~~~~~~~~~~~~~~~~
Returns the next article in a list of articles::

  get_next_article(context, article)

``get_recommended_articles``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Returns a list of all articles that have been set as recommended for this article::

  get_recommended_articles(context, article)

``load_reaction_question``
~~~~~~~~~~~~~~~~~~~~~~~~~~

Returns all reaction questions that have been linked to this article::

  load_reaction_question(context, article)

``load_user_can_vote_on_reaction_question``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Returns True or False based on whether a user has already voted on this question or this article or not::

  load_user_can_vote_on_reaction_question(context, question, article_pk)

``load_choices_for_reaction_question``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Returns all the choice that are live for a reaction question::

  load_choices_for_reaction_question(context, question)

``load_tags_for_article``
~~~~~~~~~~~~~~~~~~~~~~~~~

Returns all the tags that have been attached to this article in the CMS::

  load_tags_for_article(context, article)

``social_media_article``
~~~~~~~~~~~~~~~~~~~~~~~~

Returns the social media article::

  social_media_article(context)

Content for Tag Pages
~~~~~~~~~~~~~~~~~~~~~

``get_articles_for_tag``
~~~~~~~~~~~~~~~~~~~~~~~~

Returns all the articles that have been linked to a specific tag::

    get_articles_for_tag(context, tag)

The ``get_next_tag`` tag returns the next tag in the list of live tags. If the current tag is the last in
the list, it will return the first tag::

    get_next_tag(context, tag)

Content for CMS
~~~~~~~~~~~~~~~

The ``should_hide_delete_button`` tag returns True or False based on whether a page should be deletable or not::

    should_hide_delete_button(context, page)
