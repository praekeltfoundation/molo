Features
========

Molo consists of a core structure onto which new feature plugins can be added. This core is the foundation that allows you to create a site in Wagtail.

Core Features
-------------


- Multiple Languages
    - Molo allows you to offer you content in multiple languages using the TranslatablePageMixin
- Sections (and subsections)
    - Content sections that allows structuring of content on the site
- Articles
    - The main content element of molo.
    - It allows you to create rich articles containing multiple images, lists (bulleted/numbered) and links to other pages
- Footer pages
    - Content pages mostly used for About, Terms and Contact information
- Tags
    - Tags are words or hashtags that can be added to articles and can be used to navigate through a site.
- Reaction Questions
    - Questions that have set responses that a user can choose from. These are added to articles to get a response for a specific article.
- Banners
    - Image banners on the home page that can be linked to any page on the site
- Search
    - The ability to search for any content on the site
    - The ability to show a highlighted term in the results
    - Support for both Elastichsearch 1.x & 2.x
    - Search term highlighting using Elasticsearch Backend

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

        You need to update the ``search_results.html`` page with the following code::

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

