CHANGES
=======

11.0.8
~~~~~~
- update migrations

11.0.6
~~~~~~
- update package.json dependencies

11.0.5
~~~~~~
- flake8 on cookiecutter apps

11.0.1
~~~~~~
- Add support for Django 3+

10.2.9
~~~~~~
- Mote template fix: update invalid tag

10.2.8
~~~~~~
- Bug Fix: Don't try to delete translations for pages without a language attr

10.2.7
~~~~~~
- Bug Fix: Handle multiple returned revisions when previewing drafts

10.2.6
~~~~~~
- Add changes introduced in version 10.1.x

10.2.5
~~~~~~~
- remove password field in the "export user" admin
- Sqlite migration fix

10.2.4
~~~~~~~
- Update molo.profiles "export User" add filter for superusers

10.2.3
~~~~~~~
- Update molo.profiles "export User" admin to include multi site admin in admin list filter

10.2.2
~~~~~~~
- Disable password auto complete in Login and registration forms

10.2.1
~~~~~~~
- Add migrations to remove deprecated reaction question models

10.2.0
~~~~~~
- Deprecate reaction questions

10.1.15
~~~~~~~
- Remove validation preventing HTML from being used in MarkDown blocks
- Overwrite MarkDown block api representation to convert HTML to MarkDown

10.1.14
~~~~~~~
- Use a more lenient parser to catch HTML in MarkDown blocks

10.1.13
~~~~~~~
- Prevent HTML from being used in MarkDown blocks

10.1.12
~~~~~~~
- Update MoloPage model override wagtails can_exist_under method in case of specific_class returning None

10.1.10
~~~~~~~
- Update molo.profiles "export User" add filter for superusers

- Update molo.profiles "export User" admin to include multi site admin in admin list filter

- Disable password auto complete in Login and registration forms

10.1.9
~~~~~~
- Use request Language_code in templates

10.1.8
~~~~~~
- Update core tags(load_tags_for_article) and accommodate fake query sets for page previews

10.1.7
~~~~~~
- Enable the content API to filter articles by nav_tags

10.1.6
~~~~~~
- Fix MoloPage language attribute bug for index pages

10.1.5
~~~~~~
- Documentation updates
- Enable the API to filter article pages by live state

10.1.4
~~~~~~
- Gracefully handle Page 404's in Wagtail admin

10.1.3
~~~~~~
- Bug fixes
- Update core tags and accommodate fake querysets for page previews
- Handle key errors on registration view's form_valid method
- Update get_translation_for_cache_key
- Update security answer's check


10.1.2
~~~~~~
- Remove interactive argument from call_command function

10.1.1
~~~~~~
- Fix Content rotation's site_id bug
- Add Sitemap view to address issue in wagtails sitemap view
- Add Section's is_service_aggregator attr
- Add service_aggregator kwarg to get_sections template tag


10.1.0
~~~~~~
- Add Support for Django 2.2.5+

9.0.9
~~~~~
- Exclude Index Pages from caching

9.0.8
~~~~~
- Allow index pages to be shown without language

9.0.4
~~~~~
- Performance updates

9.0.2
~~~~~
- Merge develop to develop-9.x

9.0.1
~~~~~
- Remove wagtail forms from molo core

8.12.6
~~~~~~
- Performance updates

8.12.4
~~~~~~
- Update the robots.txt file

8.12.3
~~~~~~
- Get Tag articles template tag bug fix

8.12.2
~~~~~~
- Add the request language to the custom params in GA middleware

8.12.1
~~~~~~
- Update setting locale view redirect incase of empty next param

8.12
~~~~
- Adding a raw HTML field for the article body

8.11.9
~~~~~~
- Adding __str__ method for the timezone model

8.11.8
~~~~~~
- Fix the page serve to only redirect translated pages

8.11.7
~~~~~~
- Update the robots.txt file to exclude index pages

8.11.6
~~~~~~
- Optimisation for home page

8.11.5
~~~~~~
- Upgrade Django Rest Framework due to security vulnerability

8.11.4
~~~~~~
- Add the GSC siteSettings panel

8.11.3
~~~~~~
- Add google search console verification and setting

8.11.2
~~~~~~
- Add Page model exact_type, is_content_page helper methods

8.11.1
~~~~~~
- Add get_top_level_parent Page model method

8.11.0
~~~~~~
- Add check for Ajax submisson on Reaction Questions

8.10.9
~~~~~~
- BugFix: get_paret_section and get_next_article tags + tests

8.10.8
~~~~~~
- BugFix: Add .specific to Pages

8.10.7
~~~~~~
- BugFix: add validation check for load_child_articles_for_section

8.10.6
~~~~~~
- BugFix: get_parent_section

8.10.5
~~~~~~
- Add custom_params for unauthenticated users in the GA params

8.10.4
~~~~~~
- Add template tag for reaction question response couunt

8.10.3
~~~~~~
- Add is_via_freebasics check to template tag for bannerpages

8.10.2
~~~~~~
- Rename model fiel din migration for bannerpage (fixed clash)

8.10.0
~~~~~~
- Add richtext streamfield to Article Body
- Add freebasics check on BannerPage

8.9.5
~~~~~
- Make get_parent_section language aware

8.9.4
~~~~~
- Article ordering bug fix

8.9.3
~~~~~
- Add custom Prometheus query count decorator

8.9.1
~~~~~
- Refactor deprecating Django 2.0 code on molo.core and molo.profiles

8.9.0
~~~~~
- Add get_site() to all index pages

8.8.1
~~~~~
- BugFix: Adapted get_site() to check if site_name contains main (TEMPORARY FIX)

8.7.0
~~~~~
- Remove overriden get_url_parts method for Page

8.6.0
~~~~~
- Do not install: Broken

8.5.2
~~~~~
- BugFix: get_translation_for now works for multi site one root page

8.5.1
~~~~~
- Add feature_in_seftion filter to load_child_pages

8.5.0
~~~~~
- Add email to contact form

8.4.0
~~~~~
- Name change from topic_of_the_day to hero_article (you will need to do the same in your project code)
- Template tag added for getting sibling sections

8.3.3
~~~~~
- Add viber content panels

8.3.2
~~~~~
- Add viber sharing

8.3.1
~~~~~
- Add new social media article sharing options to template tag

8.3.0
~~~~~
- Add new social media article sharing options

8.2.0
~~~~~
- Add forms

8.1.0
~~~~~
- Add media to article for hero on homepage

8.0.4
~~~~~
- Fix molo wagtail_hooks to work with querysets

8.0.3
~~~~~
- Upgrade to Wagtail 2.2

8.0.2
~~~~~
- Update django-google-analytics-app, boto and django-storages dependencies

8.0.1
~~~~~
- Update ReadonlyPanel implementation for wagtail2

8.0.0
~~~~~
- Drop support for Python 2
- Upgrade to Wagtail 2
- These are potentially breaking changes for dependant projects that explicitly import Wagtail modules

7.1.1
~~~~~
- Fixed bug in copy to all task where article revision wasn't being saved

7.1.0
~~~~~
- Added prometheus metrics. Changes required to project see link
  https://github.com/korfuri/django-prometheus/blob/master/django_prometheus/db/common.py

7.0.9
~~~~~~
- Bug: Add pre-delete for Tag to delete all article nav tags when tag deleted

7.0.8
~~~~~~
- Added testing documentation

7.0.7
~~~~~~
- Bug: Empty tags not saved in articles

7.0.6
~~~~~~
- Bug: Update copy_language to new Translations

7.0.5
~~~~~~
- Ensure only main language pages are able to be translated

7.0.4
~~~~~~
- Ensure Show Only Translated Pages setting honours live status of page

7.0.3
~~~~~~
- Add custom_params to MoloGA middleware submit_tracking

7.0.2
~~~~~~
- Fix error in show_main_language_only() when testing if a page has a language

7.0.1
~~~~~~
- Handling added for NoneType errors

7.0.0
~~~~~~
- Molo Translations were completely refactored
- These are breaking changes, in order to upgrade to this version, once this version is on your project, before making any changes, run the management commands `add_language_to_pages`, and then run `add_translated_pages_to_pages`

6.10.0
~~~~~~
- Fix MarkDown dependency
- (this is potentially a breaking change for dependant projects that explicitly use MarkDown)

6.9.24
~~~~~~
- Update the tagged stories ordering in core_tags

6.9.23
~~~~~~
- Translation script bugfix

6.9.22
~~~~~~
- Made translation commands multisite aware

6.9.21
~~~~~~
- Add more validation to managements commands

6.9.20
~~~~~~
- Add validation to managements commands

6.9.19
~~~~~~
- BugFix: Date of birth on registration error
- BugFix: Errors in DoneForm fields

6.9.18
~~~~~~
- Add scripts for new translations

6.9.17
~~~~~~
- Add a maintenance mode middleware

6.9.16
~~~~~~
- Fix Bug in get_tag_articles template tag

6.9.15
~~~~~~
- Refactor translation lookups to reduce page load and database queries

6.9.14
~~~~~~
- add "Enable multi service directory search" Site setting field

6.9.13
~~~~~~
- Fixed unmerged commits

6.9.12
~~~~~~
- Add translation fields

6.9.11
~~~~~~
- Add nullable default service directory radius field to Site setting model

6.9.10
~~~~~~
- Fix registration form tests

6.9.9
~~~~~
- Order tagged articles by first published

6.9.8
~~~~~
- Order section articles by first published

6.9.7
~~~~~
- Fix beatifulsoup4 requirement and pin it to 4.1.0

6.9.6
~~~~~
- Order old tagged articles

6.9.5
~~~~~
- Birth date validation in molo profile not to accept future dates

6.9.4
~~~~~
- Remove old profile templates

6.9.3
~~~~~
- Update tagged articles to order from newst to oldest

6.9.2
~~~~~
- Profiles templates update
- Travis update accordingly

6.9.1
~~~~~
- Return http404 if no tag can be found
- Remove elastic-git from setup

6.9.0
~~~~~
- Only show reaction questions modeladmin to users that have can_view_response permission

6.8.4
~~~~~
- Customise: Wagtail main nav logout icon

6.8.3
~~~~~
- BugFix: Core tags - get_recommended_articles query-set value list update

6.8.2
~~~~~
- Add auth_service_uuid to UserProfile
- Fix typo on 403 page

6.8.1
~~~~~
- BugFix: assign language variable when needed for management command

6.8.0
~~~~~
- Add management command for switching the main language

6.7.7
~~~~~
- Remove overriding the model admin get_search_results

6.7.6
~~~~~
- Pin version of django-extensions to less than 2
- Add UUID to user export view and the csv
- Allow searching the users by UUID

6.7.5
~~~~~
- Install module typing for python2

6.7.4
~~~~~
- Pattern Library image icons paths update

6.7.3
~~~~~
- add rtl direction on input fields in wagtail

6.7.2
~~~~~
- Bug Fix: only return translation page if it is live

6.7.1
~~~~~
- Bug Fix: allow admins to login locally for any site

6.7.0
~~~~~
- Squash core and profile migrations to fix the issues that have arisen from migration dependency issues

6.6.4
~~~~~
- Bug Fix: Publish Pages that are scheduled when copying

6.6.3
~~~~~
- Rename profile migration 0021

6.6.2
~~~~~
- breaks down the uuid migration into 3 migrations

6.6.1
~~~~~
- Remove localisation of security questions in form

6.6.0
~~~~~
- Add UUID to molo profile
- Pin django-google-analytics to 4.2.0
- Pass UUID to Google Analytics

6.5.0
~~~~~
- Drop support for Django 1.10
- Update Node.js package electron for security fixes

6.4.3
~~~~~
- Bug Fix: support non-ascii security questions

6.4.2
~~~~~
- Bug Fix: return gender from profile and not user

6.4.1
~~~~~
- Added Gender field to Profiles Admin

6.4.0
~~~~~
- Allow multiple sites to point to one root page

6.3.2
~~~~~
- Remove untested code

6.3.1
~~~~~
- Template Changes

6.3.0
~~~~~
- Add support for Python 3.6 and Django 1.11

6.2.4
~~~~~
- Bug Fix: django-admin user view was serving a TemplateError

6.2.3
~~~~~
- Bug Fix: Fix migration dependency causing issues running on a clean database

6.2.2
~~~~~
- Bug Fix: Only create banner relations if current relations exist

6.2.1
~~~~~
- Bug Fix: Split Migrations for Timezones

6.2.0
~~~~~
- Add timezone to CMS per django install
- Bug Fix: Assign new banner link page when copying banners

6.1.5
~~~~~
- Bug Fix: Assign new article relations with copy to all

6.1.4
~~~~~
- Only return BannerPages in BannerPage tag and not any children of inheritance

6.1.3
~~~~~
- Add subtitle to BannerPage

6.1.2
~~~~~
- Add copy to all functionality

6.1.1
~~~~~
- Bug fix: Run wagtailcore migration 40 before molo core migration 34

6.1.0
~~~~~
- Official release of Molo 6
- No longer supporting Django 1.9, see upgrade considerations
  https://docs.djangoproject.com/en/2.0/releases/1.10/
- Upgraded to Wagtail 1.13x
- Molo Profiles no longer exists as a separate plugin, it now exists within Molo core

6.0.3
~~~~~
- Update develop 6x with develop

6.0.2
~~~~~
- Eliminated the use of __latest__ in migration dependencies

6.0.1
~~~~~
- Upgraded to Wagtail 1.13
- Dropped support for Django 1.9x, Now supports Django 1.10x

6.0.2-beta.1
~~~~~~~~~~~~
- Pulled latest changes from develop

6.0.1-beta.1
~~~~~~~~~~~~
- Upgraded to Wagtail 1.13

6.0.0
~~~~~~
- Upgraded to Django 1.10, No longer supporting Django 1.9
- Upgraded to Wagtail 1.10
- Profiles plugin now exists within Molo Core

5.22.5
~~~~~~
- Admin View scroller fixes

5.22.4
~~~~~~
- Admin View vertical scrolling touchpad bug fixed
- Scroller added on other Admin Views
- overlapping edit/delete controls fix on Admin View lists

5.22.3
~~~~~~
- Exclude ArticlePageLanguageProxy from being indexed
- Use strings for paths
- Run part of the test suite on Python 3

5.22.2
~~~~~~
- Fix Admin View scroller styles

5.22.1
~~~~~~
- Admin View FED bug fixes updates

5.22.0
~~~~~~
- Remove UC content import

5.21.4
~~~~~~
- Wagtail style reverts and cleanup

5.21.3
~~~~~~
- Admin View FED updates

5.21.2
~~~~~~
- Bug fix: exclude pages that are submitted for moderation from MultiSiteRedirect

5.21.1
~~~~~~
- Continued update to front end setup. See PR#465 for more details

5.21.0
~~~~~~
- Update the project setup. See PR#477 for more details
- Fix Image Hashing update bug
- Fix errant ? in URLs

5.20.0
~~~~~~
- only allow access to sites if the user has permissions for that site
Note:
- once upgrading to this version, superusers need to give non-superusers users permissions to access their relevant sites
- This release would need molo.profile 5.4.1

5.19.0
~~~~~~
- Add Facebook Analytics in Site Settings

5.18.1
~~~~~~
- Fix duplicate ImageInfo creation when image is saved

5.18.0
~~~~~~
- Update image hashing function
- Update log settings to accomodate api logs

5.17.2
~~~~~~
- Bug fix: remove update from social_media template tag

5.17.1
~~~~~~
- Allow passing obj to social_media template tag

5.17.0
~~~~~~
- Allow adding service directory api settings in CMS
- Used logging for the api import process

5.16.1
~~~~~~
- Add more caching to improve performance

5.16.0
~~~~~~
- add CSV mapping foreing page IDs to local IDs, to success email when site has been imported

5.15.0
~~~~~~
- add management command to add tag to article
- add management command to set promotion date on article
- add caching to improve performance

5.14.0
~~~~~~
- updated documentation for multi-site functionality
- add utilities to convert embedded page stream blocks in Recommended Articles
- exposed utilities via command ``move_page_links_to_recomended_articles``

5.13.1
~~~~~~
- fix image import bug which did not handle absolute URLs (i.e. storage on S3)

5.13.0
~~~~~~
- refactored importing of site content via api
- created ImageInfo model to store image hashes
- bug fixes in api endpoints
- bug fixes in site importing

5.12.0
~~~~~~
- added Migration for converting Media to MoloMedia (FIXED)

5.11.0
~~~~~~
- DO NOT ADD THIS RELEASE (Migration Faulty)
- added Migration for converting Media to MoloMedia
- added feature in homepage for MoloMedia
- fixed admin layout

5.10.0
~~~~~~
- add support for youtube links in MoloMedia

5.9.5
~~~~~
- fix admin layout styling bugs
- fix api locale field in translation when language has been deleted

5.9.4
~~~~~
- Bug Fix: Ensure load_tags_for_article only returns tags for article Pages
- Remove content_import tests

5.9.3
~~~~~
- Temporarily removed API import from sidebar

5.9.2
~~~~~
- Mote Update: Mote files updated to flexible accept applications style directory

5.9.1
~~~~~
- Bug Fix: Revert accidental travis setup change

5.9.0
~~~~~
- New Feature: API that exposes content via the `/api/v2/` url
- New Feature: Import some site content to a new site via the newly created API. Imports the following content:
  - Site languages
  - Images
  - Sections
  - Articles
  - Tags
  - Banners Pages
  - Footer Pages

5.8.2
~~~~~
- Fix the responsive styling for Admin dashboard

5.8.1
~~~~~
- Fix the styling for Admin dashboard

5.8.0
~~~~~
- Add Admin View menu with the Article View to the CMS

5.7.0
~~~~~
- Deprecate use of search backends in Molo. Use wagatailsearch instead.

5.6.0
~~~~~
- New Feature: Add Article Publish action to shortcuts

5.5.2
~~~~~
- Bug fix: ensure that the old article exist in create_new_article_relations
- Bug fix: use full path for GA tracking

5.5.1
~~~~~
- Add get_effective_banner
- Run node tests in node_js Travis environment
- Fix npm module caching
- Run against latest Node LTS release
- Allow first priority of articles on homepage to go to latest articles when tag navigation is enabled
- Bug fix: make sure the delete button is not shown in drop down menus on cms
- Bug fix: only allow voting to shown for main language page for reaction questions in cms

5.5.0
~~~~~
- Remove PyPy Travis builds
- Clean up Travis file
- Travis: push wheels (bdist_wheel) to PyPI
- Remove unused dependencies
- Move some test dependencies out of main dependencies
- Don't pin the required setuptools version
- Update LICENSE file
- Move requirements to setup.py
- Remove django-modelcluster from scaffolded app dependencies, molo.core depends on newer version already
- Allow minor updates to wagtail package (e.g. 1.9.1, not just 1.9)
- Update .gitignore to newer standard (more Python 3 friendly)
- Fix and cleanup MANIFEST.in

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

4.x
~~~

Main Features::

- Upgraded to Wagtail 1.8
- Added upload/download functionality for zipped media files
- Next and Recommended articles in articles

Backwards incompatible changes::

- Deprecatad use of ``wagtailmodeladmin``: ``wagtailmodeladmin`` package has been replaced by ``wagtail.contrib.modeladmin``
- ``wagtailmodeladmin_register`` function is replaced by ``modeladmin_register``
- ``{% load wagtailmodeladmin_tags %}`` has been replaced by ``{% load modeladmin_tags %}``
- ``search_fields`` now uses a list instead of a tuple

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
~~~~~~
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
~~~~~
- Add sitemap - include translations

4.0.2
~~~~~
- Fixed template overrides for django-admin templates

4.0.1
~~~~~
- Added upload/download functionality for zipped media files

4.0.0
~~~~~

- upgraded wagtial to 1.8
- removed external dependency on wagtailmodeladmin to use internal wagtailadmin feature
- added bulk-delete permission feature for the Moderator group
- added edit permission for Main page to moderator and editor groups

3.x
~~~

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

Backwards incompatible changes::

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
~~~~~~

- Implement custom error page for CSRF error

3.11.2
~~~~~~

- Remove automatic opening of comments when an article is promoted to Topic of the Day

3.11.1
~~~~~~

- Exclude future-dated Topic of the Day articles from Latest articles list

3.11.0
~~~~~~

- Add Support for both Elastichsearch 1.x & 2.x
- Add ability to show a highlighted term in the results

Note: Search highlighting is only supported by the Elasticsearch backend.

3.10.0
~~~~~~

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
