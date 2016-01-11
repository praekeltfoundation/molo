.. _plugins:

Features
========

Molo consists of a core structure onto which new feature plugins can be added. This core is the foundation that allows you to create a site in Wagtail.

Core Features
-------------

    - Banners
        - Image banners on the home page that can be linked to any page on the site
    - Sections (and subsections)
        - Content sections that allows structuring of content on the site
    - Articles
        - The main content element of molo.
        - It allows you to create rich articles containing multiple images, lists (bulleted/numbered) and links to other pages
    - Footer pages
        - Content pages mostly used for About, Terms and Contact information
    - Search
        - The ability to search for any content on the site
    - Multiple Languages
        - Molo allows you to offer you content in multiple languages using the Wagtail's tree structure.

Existing Plugins
----------------

The following plugins are available to extend the core features of Molo.
Please see :ref:`Installing plugins <installing-plugins>` for installation details.

.. _molo-profiles:

molo.profiles
~~~~~~~~~~~~~

``Github``: https://github.com/praekelt/molo.profiles

Profiles provides user profiles which adds registration, login and user data functionality.

This library does not provide a Django user model, it provides a profile model that can be attached to a user. Our experience is that custom User models in Django add all sorts of unpleasantries when using migrations.

Main features:
    - Loging/Registration
    - User profile to store user data

.. _molo-commenting:

molo.commenting
~~~~~~~~~~~~~~~

``Github``: https://github.com/praekelt/molo.commenting

Commenting builds on the :ref:`molo.profiles <molo-profiles>` plugin. It allows users to comment on articles and these comments to be moderated.

It is built using Django's `Comments Framework`_.

Main features:
    - Commenting on article pages
    - Moderation of comments using django-admin
    - Comment reporting by users to allow for community moderation
        - `COMMENTS_FLAG_THRESHHOLD` allows for comments to be automatically removed if they have been reported by multiple users

.. _molo-yourwords

molo.yourwords
~~~~~~~~~~~~~~

``Github``: https://github.com/praekelt/molo.yourwords

YourWords (User generated content) allows users to submit content that can be converted into an article by an admin.

Main features:
    - Setting up a Your Words competition
    - Downloading competition entries as a CSV
    - Ability to shortlist entries
    - Converting winning entries to Articles

.. _molo-polls

molo.polls
~~~~~~~~~~

.. note:: this plugin is currently in dev and not available as a standalone plugin in yet.

``Github``: https://github.com/praekelt/molo.polls


A poll is a short set of questions (or typically only one question) with predetermined answers that a user can choose from.

Main features:
    - Creating and publishing a Question to the home page
    - Multiple Question types (Single choice, Multiple Choice, Free Text, Numeric)
    - Exporting polls results as a CSV (currently in dev)

.. _`Comments Framework`: http://django-contrib-comments.readthedocs.org
