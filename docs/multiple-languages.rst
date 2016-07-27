.. _multiple-languages:

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
