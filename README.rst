Molo
====

.. include:: docs/badges.rst

.. include:: docs/getting-started.rst

Documentation
-------------

Documentation is available online at http://molo.readthedocs.org/
and in the `docs` directory of the repository.

.. |molo-docs| image:: https://readthedocs.org/projects/molo/badge/?version=latest
    :alt: Documentation
    :scale: 100%
    :target: http://molo.readthedocs.org/

To build the docs locally::

    $ virtualenv ve
    $ source ve/bin/activate
    (ve)$ pip install -r requirements-docs.txt
    (ve)$ cd docs
    (ve)$ make html

You'll find the docs in `docs/_build/index.html`
