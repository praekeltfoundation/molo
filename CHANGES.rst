CHANGE LOG
==========

3.0.3
------
- Improved performance of UC content import

3.0.2
------
- Minor bug fixes

3.0.1
------
- Minor bug fixes

3.0.0
------
- Added multi-language support
- Added content import from Universal Core content repos (using REACT)
- Renamed ``HomePage`` module to ``BannerPage``
- Updated language switcher url to include ``?next={{request.path}}``
- ``section_page.html`` now uses new template tags (see below)
- ``section_listing_homepage.html`` now uses new template tags (see below)
- Changed content structure to introduce index pages
- Added GA tag manager field to site settings
- Upgraded wagtail to 1.4.3

Backwards incompatible changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- Deprecated use of ``LanguagePage``: use ``SiteLanguage`` for multi-language support
- Deprecated use of ``Main`` : all pages are now children of their index page (e.g. Section Pages are now children of Section Index Page)
- Deprecated use of ``Section.featured_articles``: use the template tag ``{% load_descendant_articles_for_section section featured_in_section=True %}``
- Deprecated use of ``Section.featured_articles_in_homepage``: use the template tag ``{% load_descendant_articles_for_section section featured_in_homepage=True %}``
- Deprecated use of ``Section.latest_articles_in_homepage``: use the template tag ``{% load_descendant_articles_for_section section featured_in_latest=True %}``
- Deprecated use of ``Section.articles``: use the template tag ``{% load_child_articles_for_section page %}``

2.6.17
------
- Moved tasks.py to core

2.6.16
------
- Moved content rotation from cookiecutter to core

2.6.15
------
- Added automatic content rotation

2.6.14
------
- Added plugins version comparison
- Added logo as wagtail setting

2.6.13
------
- Re-release of version 2.6.12 because we forgot to increment the version
  number.

2.6.12
------
- Added metadata tag field

2.6.11
------
- Added social media fields

2.6.10
------
- Ensure CAS only applies to admin views

2.6.9
-----
- Fixed the issue with CAS not being compatible with normal login

2.6.8
-----
- Updated plugins instructions
- Updated the polls plugin in the documentation

2.6.7
-----
- core urls are not defined correctly

2.6.6
-----
- Bug fixes

2.6.5
-----
 - Added search functionality
 - Updated core templates

2.6.4
-----
 - Added support for Central Authentication Service (CAS)(CAS)

2.6.3
-----
 - Updated documentation

2.6.2
-----
 - Added missing files in the scaffold (pypi package) 2nd attempt

2.6.1
-----
 - Added missing files in the scaffold (pypi package)

2.6.0
-----
 - updated documentation
 - adding tags to ArticlePage model
 - upgraded wagtail to v1.3.1
 - better testing base for Molo

2.5.2
-----
 - Promoted articles 'featured in latest' will be ordered by most recently updated in the latest section.

2.5.1
-----
- pinned cookiecutter to version 1.0.0

2.4.2
-----
- ordering of articles within a section uses the Wagtail ordering

2.3.7
-----
- bump to official wagtail v1.0
- add health check

2.3.6
-----
- remove first_published_at from models (casuing migration issues)

2.3.3
-----
- added `extra styling hints` field to section page

2.3.2
-----
- allow articles to be featured on the homepage

2.3.1
-----
- `first published at` is not a required field

2.3.0
-----
- add homepage models
- ensure articles ordered by published date
- allow articles to be featured

2.2.1
-----
- Add images to sections
- Add support for sub sections

2.2.0
-----
- Add multi language support

2.1.1
-----
- ensure libffi-dev in sideloader build file

2.1.0
-----
- ensure libffi-dev in sideloader build file

2.1.0
-----
- Add basic models
- Add basic templates
- upgraded to v1.0b2

2.0.5
-----
- Add sideloader scripts

2.0.4
-----
- Fix cookie cutter path

2.0.3
-----
- pypi fix - include cookie cutter json

2.0.2
-----
- Use cookie cutter for a project template

2.0.1
-----
- Fix pypi package manifest

2.0.0
-----
- Initial release
