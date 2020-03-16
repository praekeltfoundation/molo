Article and Forms API
=====================
Molo extends the Wagtail API for serving content from the CMS as JSON.
This documentation will only cover additions to the functionality.
For more information please see the documentation for the
`Wagtail API <http://docs.wagtail.io/en/v2.0/advanced_topics/api/>`_

The documentation also covers endpoints added in the ``molo.forms`` plugin. This
plugin can be found on `GitHub <https://github.com/praekeltfoundation/molo.forms>`_

Articles
--------

A custom endpoint is used to ensure that draft pages will also be
returned (this is required for the content import API).

Pages endpoints
###############
    * List Endpoint ``/api/v2/pages/``

    * Detail Endpoint ``/api/v2/page/<page_id>/``

Notable ``“?type”`` options
###########################

``core.BannerPage``
*******************
Custom fields::

    title, subtitle, banner, banner_link_page, external_link

``core.ArticlePage``
********************
A special case is added to the ``MoloPageEndpoint``: If filtering with
``?type=core.ArticlePage`` then the pages can also be filtered by the ``tag`` attribute
of the ``nav_tags`` field using ``nav_tags__tag=<tag_id>``
Custom fields::

    title, subtitle, body, tags, commenting_state, commenting_open_time,
    commenting_close_time, social_media_title, social_media_description,
    social_media_image, related_sections, featured_in_latest,
    featured_in_latest_start_date, featured_in_latest_end_date, featured_in_section,
    featured_in_section_start_date, featured_in_section_end_date,
    featured_in_homepage, featured_in_homepage_start_date,
    featured_in_homepage_end_date, feature_as_hero_article, promote_date,
    demote_date, metadata_tags, latest_revision_created_at, image, social_media_image,
    social_media_description, social_media_title, nav_tags,
    recommended_articles, related_sections, go_live_at, expire_at, expired, live

``core.SectionPage``
********************
Custom fields::

    title, live, description, image, extra_style_hints, commenting_state,
    commenting_open_time, commenting_close_time, time, monday_rotation,
    tuesday_rotation, wednesday_rotation, thursday_rotation, friday_rotation,
    saturday_rotation, sunday_rotation, content_rotation_start_date,
    content_rotation_end_date, section_tags, enable_next_section,
    enable_recommended_section, go_live_at, expire_at, expired

``core.Tag``
************
Custom fields::

    id, title, feature_in_homepage, go_live_at, expire_at, expired

``forms.MoloFormPage``
**********************
Custom fields::

    live, form_fields, introduction, image, thank_you_text, allow_anonymous_submissions

``core.FooterPage``
*******************
``core.ReactionQuestion``
*************************
``core.ReactionQuestionChoice``
*******************************
``profiles.SecurityQuestionforms.PersonalisableForm``
*****************************************************

Examples
########
List endpoint:
**************
.. code-block:: json
    :linenos:

    GET /api/v2/pages/?type=core.ArticlePage&live=true

    HTTP 200 OK
    Content-Type: application/json
    {
        "meta": {
            "total_count": 10
        },
        "items": [
            {
                "id": 66,
                "meta": {
                    "type": "core.ArticlePage",
                    "detail_url": "http://api.example.com/api/v2/pages/66/",
                    "html_url": "http://api.example.com/sections/my-life/be-the-best-to-your-bestie/",
                    "slug": "be-the-best-to-your-bestie",
                    "first_published_at": "2016-09-23T17:42:31.776234+02:00"
                },
                "title": "Be the best to your bestie"
            },
            {
                "id": 72,
                "meta": {
                    "type": "core.ArticlePage",
                    "detail_url": "http://api.example.com/api/v2/pages/72/",
                    "html_url": "http://api.example.com/sections/my-life/too-many-selfies-yes-or-no/",
                    "slug": "too-many-selfies-yes-or-no",
                    "first_published_at": "2016-09-23T17:42:33.611393+02:00"
                },
                "title": "Too many selfies?"
            },

            …
        ]
    }

Detail endpoint:
****************
.. code-block:: json
    :linenos:

    GET /api/v2/pages/66/

    HTTP 200 OK
    Content-Type: application/json
    {
        "id": 66,
        "meta": {
            "type": "core.ArticlePage",
            "detail_url": "http://api.example.com/api/v2/pages/66/",
            "html_url": "http://api.example.com/sections/my-life/be-the-best-to-your-bestie/",
            "slug": "be-the-best-to-your-bestie",
            "show_in_menus": false,
            "seo_title": "",
            "search_description": "",
            "first_published_at": "2016-09-23T17:42:31.776234+02:00",
            "parent": {
                "id": 194,
                "meta": {
                    "type": "core.SectionPage",
                    "detail_url": "http://api.example.com/api/v2/pages/194/",
                    "html_url": "http://api.example.com/sections/my-life/"
                },
                "title": "My Life"
            },
            "children": null,
            "translations": [
                {
                    "id": 205,
                    "locale": "th"
                }
            ],
            "main_language_children": null
        },
        "title": "Be the best to your bestie",
        "subtitle": "Not only now, but forever",
        "body": [
            {
                "type": "paragraph",
                "value": "...",
                "id": "171e98e1-30a6-40ea-b1cf-bfcac4a853a5"
            }
        ],
        "tags": [],
        "commenting_state": null,
        "commenting_open_time": null,
        "commenting_close_time": null,
        "social_media_title": "",
        "social_media_description": "",
        "social_media_image": null,
        "related_sections": [],
        "featured_in_latest": true,
        "featured_in_latest_start_date": "2018-12-31T08:00:00.180000+02:00",
        "featured_in_latest_end_date": null,
        "featured_in_section": false,
        "featured_in_section_start_date": null,
        "featured_in_section_end_date": null,
        "featured_in_homepage": false,
        "featured_in_homepage_start_date": null,
        "featured_in_homepage_end_date": null,
        "feature_as_hero_article": false,
        "promote_date": null,
        "demote_date": null,
        "metadata_tags": [],
        "latest_revision_created_at": "2018-12-31T08:00:00.286037+02:00",
        "image": {
            "id": 308,
            "meta": {
                "type": "wagtailimages.Image",
                "detail_url": "http://api.example.com/api/v2/images/308/",
                "download_url": "http://api.example.com/21_girlpack_friendship_feature_BeTheBestToYourBestie.jpg"
            },
            "title": "21_girlpack_friendship_feature_BeTheBestToYourBestie.jpg"
        },
        "nav_tags": [
            {
                "id": 276,
                "meta": {
                    "type": "core.ArticlePageTags"
                },
                "tag": {
                    "id": 395,
                    "meta": {
                        "type": "core.Tag",
                        "detail_url": "http://api.example.com/api/v2/pages/395/"
                    },
                    "title": "friendship"
                }
            },
            …
        ],
        "recommended_articles": [
            {
                "id": 40,
                "meta": {
                    "type": "core.ArticlePageRecommendedSections"
                },
                "recommended_article": {
                    "id": 90,
                    "meta": {
                        "type": "core.ArticlePage",
                        "detail_url": "http://api.example.com/api/v2/pages/90/"
                    },
                    "title": "Do you want friends?"
                }
            }
        ],
        "go_live_at": null,
        "expire_at": null,
        "expired": false,
        "live": true
    }

Forms
-----

Molo.forms uses a custom serializer for the Form fields so that the
``forms.MoloFormPage`` detail endpoint returns the necessary information
for each field.
Available custom fields are as shown above.
The API does not currently support viewing or creating submissions for
``forms.PersonalisableForms`` as such, these are excluded from the list view.

Forms endpoints
###############
    * List Endpoint ``/api/v2/forms/``

    * Detail Endpoint ``/api/v2/forms/<page_id>/``

    * Submission Endpoint ``/api/v2/forms/<page_id>/submit_form/``

Forms Submissions
#################
A POST request to the form submission endpoint will attempt to create a
form submission object from the submitted data.
The endpoint accepts a JSON object with the input names as the attribute
keys and the user responses as the values.
An ``HTTP 201`` is returned if the submission is valid and successful.
An ``HTTP 400`` will be returned if the form being submitted to is not live,
if any of the data is invalid or if not all required fields are present.
Submissions to forms that do not have the ``allow_multiple_submissions`` set
to True will also return an ``HTTP 400`` since authentication is not
currently supported.

Examples
########

List Endpoint:
**************
.. code-block:: json
    :linenos:

    GET /api/v2/forms/?live=true

    HTTP 200 OK
    Content-Type: application/json
    {
        "meta": {
            "total_count": 8
        },
        "items": [
            {
                "id": 5,
                "meta": {
                    "type": "forms.MoloFormPage",
                    "detail_url": "http://api.example.com/api/v2/pages/5/",
                    "html_url": "http://api.example.com/sections/my-future/test-page/",
                    "slug": "test-page",
                    "first_published_at": "2020-01-20T09:33:37.736336+02:00"
                },
                "title": "test page"
            },
            {
                "id": 6,
                "meta": {
                    "type": "forms.MoloFormPage",
                    "detail_url": "http://api.example.com/api/v2/pages/6/",
                    "html_url": "http://api.example.com/sections/my-future/show-me-money/do-you-really-want-see-money/",
                    "slug": "do-you-really-want-see-money",
                    "first_published_at": "2020-01-20T15:06:01.056130+02:00"
                },
                "title": "Do you really want to see the money?"
            },
        …
        ]
    }

Detail Endpoint:
****************
.. code-block:: json
    :linenos:

    GET /api/v2/forms/5/

    HTTP 200 OK
    Content-Type: application/json
    {
        "id": 5,
        "meta": {
            "type": "forms.MoloFormPage",
            "detail_url": "http://api.example.com/api/v2/pages/5/",
            "html_url": "http://api.example.com/molo-forms/test-survey/",
            "slug": "test-survey",
            "show_in_menus": false,
            "seo_title": "",
            "search_description": "",
            "first_published_at": "2020-01-22T17:49:37.263778+02:00",
            "parent": {
                "id": 1045,
                "meta": {
                    "type": "forms.FormsIndexPage",
                    "detail_url": "http://api.example.com/api/v2/pages/5/",
                    "html_url": "http://api.example.com/molo-forms/"
                },
                "title": "Forms"
            }
        },
        "title": "Kaitlyn Test Survey [As Forms]",
        "live": true,
        "form_fields": {
            "items": [
                {
                    "id": 7,
                    "sort_order": 0,
                    "label": "How do you feel the Content Repository work is going?",
                    "required": false,
                    "default_value": "",
                    "help_text": "",
                    "page_break": false,
                    "admin_label": "how-is-work-going",
                    "choices": "Good,Not great,I'm not sure",
                    "field_type": "dropdown",
                    "input_name": "how-do-you-feel-the-content-repository-work-is-going"
                },
                {
                    "id": 8,
                    "sort_order": 1,
                    "label": "Who is working on the content repository api?",
                    "required": true,
                    "default_value": "",
                    "help_text": "",
                    "page_break": false,
                    "admin_label": "who-is-building-it",
                    "choices": "Tom,Mary,Alex",
                    "field_type": "radio",
                    "input_name": "who-is-working-on-the-content-repository-api"
                },
            …
            ]
        },
        "introduction": "The goal of the content repository work is to make content accessible across different platforms.",
        "image": {
            "id": 563,
            "meta": {
                "type": "wagtailimages.Image",
                "detail_url": "http://api.example.com/api/v2/images/563/",
                "download_url": "http://api.example.com/original_images/overcomeshyness.png"
            },
            "title": "overcomeshyness.png"
        },
        "thank_you_text": "Great! Thanks for being involved in this demo!",
        "allow_anonymous_submissions": true
    }

Submission Endpoint:
********************
.. code-block:: json
    :linenos:

    POST /api/v2/forms/5/submit_form/
    {
        "how-do-you-feel-the-content-repository-work-is-going": "Good",
        "who-is-working-on-the-content-repository-api": "Alex"
    }

    HTTP 201 CREATED
    Content-Type: application/json

    {
        "how-do-you-feel-the-content-repository-work-is-going": "Good",
        "who-is-working-on-the-content-repository-api": "Alex",
    }
