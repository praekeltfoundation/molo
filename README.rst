django-skeleton
===============

A Sample Django application that illustrates what bits make up a
sane Django based web app deployment.

::

    $ virtualenv ve
    $ source ve/bin/activate
    (ve)$ pip install -r requirements.pip


The following packages are included:

South
-----

South_ manages your schema and data migrations well enough.
As part of a deploy we expect any schema changes needed
to be part of your repository and handled by south.

For your initial schema::

    (ve)$ ./manage.py schemamigration --initial <app-name>

For subsequent schema changes::

    (ve)$ ./manage.py schemamigration --auto <app-name>

The schema changes can be applied manually with::

    (ve)$ ./manage.py migrate

Or generally what happens as part of a deploy is::

    (ve)$ ./manage.py syncdb --noinput --no-initial-data --migrate


.. _South: http://south.aeracode.org/