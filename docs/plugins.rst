Plugins
===============

Installing Plugins
------------------

Molo plugins are normal python modules and can be installed using pip.

If you didn't include the app during the scaffolding step using
``molo scaffold myapp --include=molo.profiles ^profiles/`` and you wish to add it manually,
complete the following steps:

Install the plugin using pip::

    $ pip install molo.profiles

Add the new plugin to your ``INSTALLED_APPS`` in your ``myapp/settings/base.py``::

    INSTALLED_APPS = (
        ...
        'molo.profiles',
    )

Then add the new plugin urls to your ``myapp/urls.py``::

    url(r'^polls/', include('polls.urls', namespace='molo.polls')),

The final step is to run migrations as the plugins usually have their own migrations::

    $ ./manage.py migrate

Existing Plugins
----------------

The following plugins are available to extend the core features of Molo.

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
    - ``COMMENTS_FLAG_THRESHHOLD`` allows for comments to be automatically removed if they have been reported by multiple users

molo.surveys
~~~~~~~~~~~~

``Github``: https://github.com/praekelt/molo.surveys/

Surveys allows for user feedback on content.

Main Features:
    - Multiple Questions of various types
    - Multi-page surveys
    - Direct and Linked surveys

molo.yourwords
~~~~~~~~~~~~~~

``Github``: https://github.com/praekelt/molo.yourwords

YourWords (User generated content) allows users to submit content that can be converted into an article by an admin.

Main features:
    - Setting up a Your Words competition
    - Downloading competition entries as a CSV
    - Ability to shortlist entries
    - Converting winning entries to Articles

molo.polls
~~~~~~~~~~


``Github``: https://github.com/praekelt/molo.polls


A poll is a short set of questions (or typically only one question) with predetermined answers that a user can choose from.

Main features:
    - Creating and publishing a Question to the home page, section page and article page
    - Multiple Question types (Single choice, Multiple Choice, Free Text, Numeric)
    - Exporting polls results as a CSV (currently in dev)

.. _`Comments Framework`: http://django-contrib-comments.readthedocs.org

molo.usermetadata
~~~~~~~~~~~~~~~~~


``Github``: https://github.com/praekelt/molo.usermetadata


User meta data allows one to create persona pages so that when a user visits a site for the first time,
they are able to choose a persona, or choose to skip this.
This does not require the user to log in.

Main features:
    - Creating and publishing persona pages to be displayed when the user visits the site for the first time
