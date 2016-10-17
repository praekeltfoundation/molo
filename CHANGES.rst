CHANGE LOG
==========

3.x
---

Major revamp to the way we handle Multi Language on Molo and a bunch of new features

Main features::

- Revamped Multi Language support
- We added content automated content rotation and a way to schedule when content should be cycled
- We now offer specifying Google Analytics from the CMS for both GA and GTM (this uses celery for GA)
- Renamed HomePage module to BannerPage
- Changed content structure to introduce index pages
- Upgraded wagtail to 1.4.3
- We've added the option to allow un-translated pages to be hidden
- We now show a translated page on the front end when it's main language page is unpublished
- Add Topic of the Day functionality
- Add Support for both Elastichsearch 1.x & 2.x
- Add ability to show a highlighted term in the results

Backwards incompatible changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- Deprecated use of ``LanguagePage``: use ``SiteLanguage`` for multi-language support
- Deprecated use of ``Main`` : all pages are now children of their index page (e.g. Section Pages are now children of Section Index Page)
- Deprecated use of ``Section.featured_articles``: use the template tag ``{% load_descendant_articles_for_section section featured_in_section=True %}``
- Deprecated use of ``Section.featured_articles_in_homepage``: use the template tag ``{% load_descendant_articles_for_section section featured_in_homepage=True %}``
- Deprecated use of ``Section.latest_articles_in_homepage``: use the template tag ``{% load_descendant_articles_for_section section featured_in_latest=True %}``
- Deprecated use of ``Section.articles``: use the template tag ``{% load_child_articles_for_section page %}``

3.11.1
~~~~~

- Exclude future-dated Topic of the Day articles from Latest articles list

3.11.0
~~~~~

- Add Support for both Elastichsearch 1.x & 2.x
- Add ability to show a highlighted term in the results
Note: Search highlighting is only supported by the Elasticsearch backend.

3.10.0
~~~~~

- Add Topic of the Day functionality

3.9.2
~~~~~

- Set GOOGLE_ANALYTICS to None in settings

3.9.1
~~~~~

- Fix the issue with switching between child languages
- Fix the issue with allowing articles to exist in multiple sections

3.9.0
~~~~~

- Update user permissions

3.8.2
~~~~~

- Ensure title is filled in for GA middleware

3.8.0
~~~~~

- Add custom GA celery middleware
- Use celery for GA instead of gif pixel

3.7.5
~~~~~

- Add middleware to ignore accept language header

3.7.4
~~~~~

- Return the language code for languages that are not supported

3.7.3
~~~~~

- Make sure Locales are not restricted to 2 char codes and we can use the country code

3.7.2
~~~~~

- Return the language code for languages that babel is not supporting

3.7.1
~~~~~

- Make sure unpublished translated pages are not appearing on front end

3.7.0
~~~~~

- Show the translated page on front end when it's main language page is unpublished

3.6.0
~~~~~

- Add the option that untranslated pages will not be visible to the front end user when they viewing a child language of the site

3.5.0
~~~~~

- Add date and time options to content rotation

3.4.2
~~~~~

- Fixed Migration Bug

3.4.1
~~~~~

- Add GA urls to Molo Urls
- Pinned Flake8 to 2.6.2

3.4.0
~~~~~

- Add local and global GA tracking codes

3.3.0
~~~~~

- Add random content rotation for articles featured on homepage

3.2.8
~~~~~

- Add global GA Tag model

3.2.7
~~~~~

- Add get_translation template tag

3.2.6
~~~~~

- Delete the translated page when a page is deleted

3.2.5
~~~~~

- Return Marathon app & version information in the health checks.

3.2.4
~~~~~~

- Default count for sections set to 0

3.2.3
~~~~~~

- Add session key middleware for each user to use with GTM when javascript is disabled

3.2.2
~~~~~~

- Handling import * error with noqa

3.2.1
~~~~~~

- Delete translated page when a page is deleted
- Added extra lang info for languages that django doesn't support

3.2.0
~~~~~~

- Added wagtail multimedia support
- Allow articles to exist in multiple sections

3.1.11
~~~~~~

- Fixed bugs with UC content importing, Arabic slugs and path issue

3.1.10
~~~~~~
- Fixed another small bug with UC content validation

3.1.9
~~~~~~
- Fixed a bug with UC content validation

3.1.8
~~~~~~
- Limit import content to users belonging to `Universal Core Importers` group

3.1.7
~~~~~~
- Content validation now happens in a celery task

3.1.6
~~~~~~
- Added pagination for articles in section
- Show the active language and display the local name
- Added load_sections template tag

3.1.5
~~~~~~
- Importing validation errors to be shown in the UI for celery task

3.1.4
~~~~~~
- Upgraded wagtail to 1.4.5
- Effective style hint to support multi-language

3.1.3
~~~~~~
- Content import now happens in a celery task

3.1.2
~~~~~~
- Added templates for forgot password

3.1.1
~~~~~~
- Pined django-cas-ng to 3.5.4

3.1.0
~~~~~~
- Upgraded to Django 1.9 and Wagtail 1.4.4

3.0.3
~~~~~~
- Improved performance of UC content import

3.0.2
~~~~~~
- Changed molo.core version number in get_pypi_version test

3.0.1
~~~~~~
- Changed molo.core version number in versions_comparison test

3.0.0
~~~~~~
- Added multi-language support
- Added content import from Universal Core content repos (using REACT)
- Renamed ``HomePage`` module to ``BannerPage``
- Updated language switcher url to include ``?next={{request.path}}``
- ``section_page.html`` now uses new template tags (see below)
- ``section_listing_homepage.html`` now uses new template tags (see below)
- Changed content structure to introduce index pages
- Added GA tag manager field to site settings
- Upgraded wagtail to 1.4.3


2.x
---

This is the initial release of Molo (1.x was considered beta)

Main features::

- Scafolding a Wagtail site with basic models
- Core features including Banners, Sections, Articles, Footer Pages, Search
- Out the box support for plugins (molo.profiles, molo.commenting, molo.yourwords, molo.polls)
- Upgraded Wagtail to 1.0

2.6.17
~~~~~~
- Moved tasks.py to core

2.6.16
~~~~~~
- Moved content rotation from cookiecutter to core

2.6.15
~~~~~~
- Added automatic content rotation

2.6.14
~~~~~~
- Added plugins version comparison
- Added logo as wagtail setting

2.6.13
~~~~~~
- Re-release of version 2.6.12 because we forgot to increment the version
  number.

2.6.12
~~~~~~
- Added metadata tag field

2.6.11
~~~~~~
- Added social media fields

2.6.10
~~~~~~
- Ensure CAS only applies to admin views

2.6.9
~~~~~
- Fixed the issue with CAS not being compatible with normal login

2.6.8
~~~~~
- Updated plugins instructions
- Updated the polls plugin in the documentation

2.6.7
~~~~~
- core urls are not defined correctly

2.6.6
~~~~~
- Bug fixes

2.6.5
~~~~~
 - Added search functionality
 - Updated core templates

2.6.4
~~~~~
 - Added support for Central Authentication Service (CAS)(CAS)

2.6.3
~~~~~
 - Updated documentation

2.6.2
~~~~~
 - Added missing files in the scaffold (pypi package) 2nd attempt

2.6.1
~~~~~
 - Added missing files in the scaffold (pypi package)

2.6.0
~~~~~
 - updated documentation
 - adding tags to ArticlePage model
 - upgraded wagtail to v1.3.1
 - better testing base for Molo

2.5.2
~~~~~
 - Promoted articles 'featured in latest' will be ordered by most recently updated in the latest section.

2.5.1
~~~~~
- pinned cookiecutter to version 1.0.0

2.4.2
~~~~~
- ordering of articles within a section uses the Wagtail ordering

2.3.7
~~~~~
- bump to official wagtail v1.0
- add health check

2.3.6
~~~~~
- remove first_published_at from models (casuing migration issues)

2.3.3
~~~~~
- added `extra styling hints` field to section page

2.3.2
~~~~~
- allow articles to be featured on the homepage

2.3.1
~~~~~
- `first published at` is not a required field

2.3.0
~~~~~
- add homepage models
- ensure articles ordered by published date
- allow articles to be featured

2.2.1
~~~~~
- Add images to sections
- Add support for sub sections

2.2.0
~~~~~
- Add multi language support

2.1.1
~~~~~
- ensure libffi-dev in sideloader build file

2.1.0
~~~~~
- ensure libffi-dev in sideloader build file

2.1.0
~~~~~
- Add basic models
- Add basic templates
- upgraded to v1.0b2

2.0.5
~~~~~
- Add sideloader scripts

2.0.4
~~~~~
- Fix cookie cutter path

2.0.3
~~~~~
- pypi fix - include cookie cutter json

2.0.2
~~~~~
- Use cookie cutter for a project template

2.0.1
~~~~~
- Fix pypi package manifest

2.0.0
~~~~~
- Initial release
