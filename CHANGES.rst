CHANGE LOG
==========
3.0rc10
------
- Added multi-languages support for search

3.0rc9
------
- Pined django-cas-ng version to 3.5.3

3.0rc8
------
- Update import API to support multiple repos
- Update import API to support fetching repos from site url
- Update import UI to support multiple repos
- Changed content structure to introduce index pages

Backwards incompatible changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- deprecated use of ``Main`` : all pages are now children of their index page (e.g. Section Pages are now children of Section Index Page)

3.0rc7
------
- Add GA tag manager field to site settings

3.0rc6
------
- Remove commenting settings from the BannerPage model

3.0rc5
------
- Re-release of version 3.0rc3 because we forgot to increment the version
  number.

3.0rc3
------
- Bug fixes

3.0rc2
------
- Fixed migration conflict

3.0rc1
------
- added multilanguage support
- added content import from UC content repos (using REACT)
- rename ``HomePage`` module to ``BannerPage``
- upgrade wagtail to 1.4.1
- updated language switcher url to include ``?next={{request.path}}``
- ``section_page.html`` now uses new template tags (see below)
- ``section_listing_homepage.html`` now uses new template tags (see below)

Backwards incompatible changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- deprecated use of ``LanguagePage``: all pages are now direct children of ``Main`` (use ``SiteLanguage`` for multilanguage support)
- deprecated use of ``Section.featured_articles``: use the template tag ``{% load_descendant_articles_for_section section featured_in_section=True %}``
- deprecated use of ``Section.featured_articles_in_homepage``: use the template tag ``{% load_descendant_articles_for_section section featured_in_homepage=True %}``
- deprecated use of ``Section.latest_articles_in_homepage``: use the template tag ``{% load_descendant_articles_for_section section featured_in_latest=True %}``
- deprecated use of ``Section.articles``: use the template tag ``{% load_child_articles_for_section page %}``

2.6.15
------
- Add random content rotation

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
