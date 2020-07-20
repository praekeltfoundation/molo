What is bundled with Molo?
==========================

1. `Wagtail CMS`_
2. `Molo Profiles`_
3. Basic feature phone template set.
4. Basic models for the following tree structure:

   1. A site has a main language, and the option of one or more additional languages.
        - All content has to initially be created in the main language. Thereafter translations can be made for that content.
        - Translations for content cannot exist for additional languages if it does not first exist for the main language.
        - The first language added will be the main language, any other languages added after will be additional languages.

    .. image:: ./_static/images/main_language.png

   2. Once a main language has been created, a main page will be created as well. A main page consists of index pages.
        - Index pages exist for each content type.
        - All section pages are grouped into the 'Sections' index page.
        - All banners are grouped into the 'Banners' index page.

    .. image:: ./_static/images/indexes.png

   3. Once a section is made, articles can then be added to that section.
        - Articles only exist as a child of a section page.
        - Articles are composed from one or more blocks.
        - Blocks can be headings, paragraphs, images, lists or links to other pages.

    .. image:: ./_static/images/article_blocks.png

   4. Content such as sections or articles are displayed in their main language. Their translation in any additional language added is shown below the content. If one would like to edit the Spanish version of 'Staying Healthy', one would click on 'SPANISH', and then edit.

    .. image:: ./_static/images/translation.png

   5. A Settings tab that includes Site Settings. Site Settings is where the logo, google analytics and various other settings are set.

    .. image:: ./_static/images/site_settings.png


.. _`Wagtail CMS`: http://wagtail.io
.. _`Molo Profiles`: https://github.com/praekeltfoundation/molo.profiles/tree/develop/molo/profiles
