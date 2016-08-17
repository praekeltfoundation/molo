.. _multiple-languages:
.. _template-tags:

Multiple Languages
==================

Molo features the ability to create translatable pages. This means that pages such as a section or article can be translatable. This is done via adding the TranslatablePageMixin in the Page's definition.

Creating A Translatable Page Model
----------------------------------
In your models.py import the TranslatablePageMixin::

    from molo.core.models import TranslatablePageMixin

Add it to the definition of your model::

    class Competition(TranslatablePageMixin, Page):
      description = models.TextField(null=True, blank=True)

Getting Translations
--------------------
In order to get the translations for a page model we use the following helper functions from the TranslatablePageMixin.
Given a locale, this will return the translation of the page::

    competition.get_translation_for(locale)

We use template tags to get the locale.

The following will return the main language that the content was created in, if the content is currently in any additional language.
For example, if the content is currently in French, and the main language is English, this function will return English as the main language::

    competition.main_language_page
