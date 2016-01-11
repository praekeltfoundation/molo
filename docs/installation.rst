.. _installation:

Installation
============

Molo requires `Python`_ (version 2.6 or 2.7) to be installed. This installation method also requires `pip`_. Both of these must be installed before following the installation steps below.

Installing Molo
---------------

Molo can be then installed using::

   $ pip install molo.core

.. _installing-plugins:

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

    $ ./manage.py test

.. _python: https://www.python.org/
.. _pip: https://pip.pypa.io/en/latest/index.html
