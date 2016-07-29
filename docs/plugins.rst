.. _plugins:
.. _multiple-languages:
.. _template-tags:

Plugins
===============

Installing Plugins
------------------

Molo plugings are normal python modules and can be installed using pip::

    $ pip install molo.profiles

Next, you'll need to add the new plugin to your ``INSTALLED_APPS`` in your ``myapp/settings/base.py`` (if you did't include it during the scaffolding step using ``molo scaffold myapp --include=molo.profiles ^profiles/``)::

    INSTALLED_APPS = (
        ...
        'molo.profiles',
    )

Next, you'll need to add the new plugin urls to your ``myapp/urls.py`` (if you didn't include it during the scaffolding step using ``molo scaffold myapp --include=molo.profiles ^profiles/``)::

    url(r'^polls/', include('polls.urls', namespace='molo.polls')),

The final step is to run migrations as the plugins usually have their own migrations::

    $ ./manage.py migrate
