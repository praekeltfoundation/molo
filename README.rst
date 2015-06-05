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

Tests
-----

Make sure to install the requirement development & testing dependencies::

   $ pip install -r requirements-dev.txt

And then run the full test suite with::

   $ ./run-tests.sh
