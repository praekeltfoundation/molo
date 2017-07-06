.. _merged-cms:
.. _molo_bundle:
.. _template-tags:

Merged CMS
==========

Molo allows you to manage more than one site in a single CMS using wagtail's multi-site functionality.

Sharing a database
------------------

The database is shared between the number of sites you have. It is important to
know this when querying data. One should always make sure the page/s you are querying
for are descendants of the correct Main page.

See wagtail documentation for more on Multi-Site CMS
https://wagtail.io/blog/multi-site-wagtail/

Copying between sites with multi-language content
-------------------------------------------------

Molo allows you to create content in multiple languages, as well as have sites
in multiple languages. When copying content in language x and y to a site that
has only language x, the content will be copied over as well as language y.
However, language y will be set as inactive as it never existed on the desination
site before the copy.

See help centre docs for more info on copying content and sites
(insert link to helpcentre docs)
