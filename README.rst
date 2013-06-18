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

As an example, the sample ``app1`` application's migrations were created
with the following commands after creating the ``app1/models.py`` file::

    (ve)$ ./manage.py schemamigration --initial app1
    Creating migrations directory at '.../django-skeleton/app1/migrations'...
    Creating __init__.py in '.../app1/migrations'...
     + Added model app1.App1Model
    Created 0001_initial.py. You can now apply this migration with: ./manage.py migrate app1

A later change to the model definition is detected by South_ and a new
schema migration is generated to reflect this change.

    (ve)$ ./manage.py schemamigration --auto app1
     + Added field gender on app1.App1Model
    Created 0002_auto__add_field_app1model_gender.py.
    You can now apply this migration with: ./manage.py migrate app1


.. _South: http://south.aeracode.org/