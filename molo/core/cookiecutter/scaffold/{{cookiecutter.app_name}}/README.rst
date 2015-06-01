{{cookiecutter.app_name}}
=========================

This is an application scaffold for Molo_.

Getting started
---------------

To get started, clone the repo from git::

    $ virtualenv ve
    $ pip install -e .
    $ ./manage.py migrate
    $ ./manage.py createsuperuser
    $ ./manage.py runserver

You can now connect access the demo site on http://localhost:8000


.. _Molo: https://molo.readthedocs.org
