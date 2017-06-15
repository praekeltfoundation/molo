CHANGE LOG
==========

5.4.7
~~~~~
- Update static files to fix missing/incorrect references

5.4.6
~~~~~
- Increase character limit on reaction question success message

5.4.5
~~~~~
- Add reaction question success_messages

5.4.4
~~~~~
- Add `get_effective_image` to reaction question choices

5.4.3
~~~~~
- Fix a bug for `get_next_tag` template tag

5.4.2
~~~~~
- show correct articles for language in load more and next tag on tag page

5.4.1
~~~~~
- Add get_next_tag Template Tag
- Add admin views for Reaction Questions
- Add util for creating new article relations when copying

5.4.0
~~~~~
- Add load more for Search Page
- Add load more for Tag Page
- Add reaction questions basic functionality

5.3.1
~~~~~
- Use get_effective_image instead of image in templates

5.3.0
~~~~~
- Add load more functionality to section page

5.2.5
~~~~~
- Bug Fix: Only index tag list if list not empty for sections and tags

5.2.4
~~~~~
- Bug Fix: Only show articles in search results
- Bug Fix: Only index tag list if list not empty

5.2.3
~~~~~
- Bug Fix: Show translation for Section Page on Home Page
- Bug Fix: Only show articles relevant to site under a tag
- Bug Fix: Ensure new article tag relations are made when copying sites

5.2.2
~~~~~
- Added Positional Banner Pages functionality
- Bug Fix: Return Main language pages for latest articles

5.2.1
~~~~~
- Added Tags to SectionPage
- Added Load More functionality for ArticlePages on the homepage


5.2.0
~~~~~
- Add gef_effective_image for ArticlePage (returns the image of article's main language page if article has no image, else returns article's image)
- Add get_parent template tag (returns the parent of a page)
- Bug fix: Filter tags via descendant of main
- Bug fix: Use 'to' id directly for copying in celery


5.1.1
~~~~~
- Bug fix: Call correct template for tag navigation
- Bug fix: Only call translation hook for translatable pages

5.1.0
~~~~~
- Add basics and components for Springster
- Add tag navigation
- Add better error handling for copying section index contents

5.0.4
~~~~~
- Use celery for copying section index contents

5.0.3
~~~~~
- Add parent_page_types to SectionPage

5.0.2
~~~~~
- Fix test for admin url redirect

5.0.1
~~~~~
- Version bump for molo profiles to resolve pin dependencies

5.0.0
~~~~~
- Pin molo.profiles to latest version
- Move templates out from cookiecutter
- Implement pattern library components to templates
- Add Mote to cookiecutter
- Fix of previous release
- Added index creation signals
- Added non routable mixin for Surveys
- Added profiles urls
- Added multi-site cms functionality (Merged CMS)
- Added authentication backend for linking users to sites
- Added middleware for site redirect

4.4.13
~~~~~~
- Insure content demotion happens for each section individually

4.4.12
~~~~~~
- Remove promotion settings from footer pages

4.4.11
~~~~~~
- Fixed content import to return all data and not just default 10

4.4.10
~~~~~
- Fixed recommended article ordering in templatetag logic

4.4.9
~~~~~
- Added Non routable page mixin

4.4.8
~~~~~
- Pulled in changes from previous versions that were accidentally excluded
- Consolidated celery tasks in base settings file

4.4.7
~~~~~
- Fixed random test failures in content rotation test

4.4.6
~~~~~
- consolidate minute tasks into 1 call

4.4.5
~~~~~
- consolidate minute tasks into 1 call

4.4.4
~~~~~
- Fixed bug for previewing pages

4.4.3
~~~~~
- Excluded metrics URL from Google Analytics
- Fixed access to Explorer bug for superuser's with non-superuser roles

4.4.2
~~~~~
- Allows content rotation to pick from descendant articles not only child articles

4.4.1
~~~~~
- Updated template overrides to fix missing Page admin buttons

4.4.0
~~~~~
- Content rotation enhancement:
- Only promote pages that are exact type of ArticlePage
- Only demote an article if there is more than two promoted articles

4.3.3
~~~~~
- Add django clearsessions to celery tasks

4.3.2
~~~~~
- Added missing classes in custom admin template

4.3.1
~~~~~
- Fixed template error

4.3.0
~~~~~
- Removed the ability to delete index pages using the admin UI

4.2.0
~~~~~
- added multi-language next and recommended article feature

4.1.0
~~~~~~
- Add sitemap - include translations

4.x
---

Main Features::

- Upgraded to Wagtail 1.8
- Added upload/download functionality for zipped media files
- Next and Recommended articles in articles

Backwards incompatible changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- Deprecatad use of ``wagtailmodeladmin``: ``wagtailmodeladmin`` package has been replaced by ``wagtail.contrib.modeladmin``
- ``wagtailmodeladmin_register`` function is replaced by ``modeladmin_register``
- ``{% load wagtailmodeladmin_tags %}`` has been replaced by ``{% load modeladmin_tags %}``
- ``search_fields`` now uses a list instead of a tuple

4.0.2
~~~~~~
- Fixed template overrides for django-admin templates

4.0.1
~~~~~~
- Added upload/download functionality for zipped media files

4.0.0
~~~~~~

- upgraded wagtial to 1.8
- removed external dependency on wagtailmodeladmin to use internal wagtailadmin feature
- added bulk-delete permission feature for the Moderator group
- added edit permission for Main page to moderator and editor groups

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
- Implement custom error page for CSRF error

Backwards incompatible changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- Deprecated use of ``LanguagePage``: use ``SiteLanguage`` for multi-language support
- Deprecated use of ``Main`` : all pages are now children of their index page (e.g. Section Pages are now children of Section Index Page)
- Deprecated use of ``Section.featured_articles``: use the template tag ``{% load_descendant_articles_for_section section featured_in_section=True %}``
- Deprecated use of ``Section.featured_articles_in_homepage``: use the template tag ``{% load_descendant_articles_for_section section featured_in_homepage=True %}``
- Deprecated use of ``Section.latest_articles_in_homepage``: use the template tag ``{% load_descendant_articles_for_section section featured_in_latest=True %}``
- Deprecated use of ``Section.articles``: use the template tag ``{% load_child_articles_for_section page %}``

3.17.4
~~~~~~

- Fix the bug with draft article publishing when content rotation is on

3.17.3
~~~~~~

- Ensure email address is set when using SSO

3.17.2
~~~~~~

- Put ForceDefaultLanguageMiddleware before django.middleware.locale.LocaleMiddleware

3.17.1
~~~~~~

- (bug) use datetime instead of UTC timezone for rotation

3.17.0
~~~~~~

- Add celery task for publishing pages

3.16.2
~~~~~~

- (bug) content rotation on homepage

3.16.1
~~~~~~

- (bug) only show published articles on front end

3.16.0
~~~~~~

- Add promote and demote dates to article promotion setting
- Remove boolean promotion options
- Data migration to set all articles with feature ticks to have a promotion start date
- Order articles by promotion date

3.15.0
~~~~~~

- Enable the sharing of articles to Facebook and Twitter from the article page.

3.14.1
~~~~~~

- Change create to get_or_create in migration 47

3.14.0
~~~~~~

- Redefine core permissions for groups

3.13.0
~~~~~~

- Add clickable front-end tags to articles

3.12.3
~~~~~~

- Add migrations for external link

3.12.2
~~~~~~

- Signal on page moving and Allow adding external link to banner page

3.12.1
~~~~~~

- (bug) search URL was defined using the wrong regex (it broke Service Directory plugin)

3.12.0
~~~~~

- Implement custom error page for CSRF error

3.11.2
~~~~~

- Remove automatic opening of comments when an article is promoted to Topic of the Day

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

3.8.3
~~~~~

- Ensure title is encoded properly for GA

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
