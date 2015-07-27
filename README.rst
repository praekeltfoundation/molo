Molo
====

.. image:: https://travis-ci.org/praekelt/molo.svg?branch=develop
    :target: https://travis-ci.org/praekelt/molo
    :alt: Continuous Integration

.. image:: https://coveralls.io/repos/praekelt/molo/badge.png?branch=develop
    :target: https://coveralls.io/r/praekelt/molo?branch=develop
    :alt: Code Coverage

.. image:: https://readthedocs.org/projects/molo/badge/?version=latest
    :target: https://molo.readthedocs.org
    :alt: Molo Documentation

.. image:: https://badge.fury.io/py/molo.core.svg
    :target: http://badge.fury.io/py/molo.core
    :alt: Pypi Package

Molo is a set of tools for publishing mobi sites with a community focus.
It scaffolds a Django application for you with sensible defaults, packages
and configuration to help you get going as soon as possible:

The goal of Molo is to provide a solid base of proven, stable packages that
help Praekelt Foundation and partners to deliver on project scope::

   $ pip install molo.core
   $ molo scaffold myapp
   $ cd myapp/
   $ ./manage.py migrate
   $ ./manage.py createsuperuser
   $ ./manage.py runserver

Open the sample site in your browser at http://localhost:8000/ and the CMS
at http://localhost:8000/admin/.

What you have now is a standard Django application set up for normal
development like outlined in the Django documentation. The only main difference
is that your settings are Python modules found in the
``settings/dev.py`` and ``settings/production.py`` files in your applications
folder. Both of these inherit settings from ``settings/base.py``.

To create your own custom settings add a ``local.py`` file in the ``settings``
folder. The ``settings/dev.py`` will automatically include those settings
for your local development environment.

Now develop your application and write tests for the features you add.
Running your tests for Django works as you would expect::

   $ ./manage.py test

What is bundled with Molo?
--------------------------

1. Basic feature phone template set.
2. Basic models for the following tree structure:

   1. A site has languages
   2. A language has a homepage
   3. Articles are organised into sections.
   4. Articles are composed from one or more blocks.
   5. Blocks can be headings, paragraphs, images, lists or
      links to other pages.

Testing the Molo scaffolding tool
---------------------------------

If you're interested in working on or contributing to the code that
does the scaffolding then clone this repository from the GitHub repository at
http://github.com/praekelt/molo.

Install the requirement development & testing dependencies::

   $ pip install -r requirements-dev.txt

And then run the full test suite with::

   $ ./run-tests.sh

Pull requests are expected to follow Praekelt's `Ways Of Working`_.

.. _`Ways of Working`: http://ways-of-working.rtfd.org
