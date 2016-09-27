.. _plugins:
.. _template-tags:

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
        - The ability to show a highlighted term in the results
        - Support for both Elastichsearch 1.x & 2.x

.. note:: Search highlighting is only supported by the Elasticsearch backend.
        
        You can use Elasticsearch 1 with the following settings::

            WAGTAILSEARCH_BACKENDS = {
                'default': {
                    'BACKEND': 'molo.core.wagtailsearch.backends.elasticsearch',
                    'INDEX': 'base',
                },
            }

        Or Elasticsearch 2::

            WAGTAILSEARCH_BACKENDS = {
                'default': {
                    'BACKEND': 'molo.core.wagtailsearch.backends.elasticsearch2',
                    'INDEX': 'base',
                },
            }
        
        The example below shows how to show the highlighted word in the search results page with the following rules:

        1. Title field is always displayed: if the term appears in this field, it will be highlighted.
        2. Display highlighted term in subtitle or body. If the term appears in the title only, display the original content of the subtitle field.

        You need to update the `search_results.html` page with the following code::

            {% for page in search_results %}
              {% with parent_section=page.get_parent_section ancestor=page.get_parent_section.get_ancestors.last %}
                <a href="{% pageurl page %}">
                  <div class="nav">
                    {% if ancestor.sectionpage.image %}
                        <h6>{{ancestor.title}}</h6>
                    {% else %}
                        <h6>{{parent_section.title}}</h6>
                    {% endif %}
                    {% if page.title_highlight %}
                        <h3>{{page.title_highlight|safe}}</h3>
                    {% else %}
                        <h3>{{page.title}}</h3>
                    {% endif %}
                    {% if page.subtitle_highlight or page.body_highlight %}
                        {% if page.subtitle_highlight %}
                            <p>{{page.subtitle_highlight|safe}}</p>
                        {% elif page.body_highlight %}
                            <p>{{page.body_highlight|safe}}</p>
                        {% endif %}
                    {% else %}
                        <p>{{page.subtitle}}</p>
                    {% endif %}
                  </div>
                </a>
              {% endwith %}
            {% endfor %}


    - Multiple Languages
        - Molo allows you to offer you content in multiple languages using the TranslatablePageMixin


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


``Github``: https://github.com/praekelt/molo.polls


A poll is a short set of questions (or typically only one question) with predetermined answers that a user can choose from.

Main features:
    - Creating and publishing a Question to the home page, section page and article page
    - Multiple Question types (Single choice, Multiple Choice, Free Text, Numeric)
    - Exporting polls results as a CSV (currently in dev)

.. _`Comments Framework`: http://django-contrib-comments.readthedocs.org

.. _molo-usermetadata

molo.usermetadata
~~~~~~~~~~~~~~~~~


``Github``: https://github.com/praekelt/molo.usermetadata


User meta data allows one to create persona pages so that when a user visits a site for the first time, they are able to choose a persona, or choose to skip this. This does not require the user to log in.

Main features:
    - Creating and publishing persona pages to be displayed when the user visits the site for the first time
