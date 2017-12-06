CHANGE LOG
==========

5.4.3
-----
- Remove randomizing the questions

5.4.2
-----
- Bug Fix: show an error on frontend if the user did answer the security question on registration when they try to reset their password
- Won't be able to delete a security question when users have used it

5.4.1
-----
- Bug Fix: enable search via username on permissions

5.4.0
-----
- Add site permissions to admin users

5.3.3
-----
- Bug Fix: Filter Security Questions by site

5.3.2
-----
- Bug Fix: Add null check in backend for CAS

5.3.1
-----
- Bug Fix: Create security questions under correct index

5.3.0
-----
- add import export functionality for users and security questions

5.2.0
-----
- add registration token on user profile for fcm

5.1.0
-----
- ensure request is passed on to AuthenticationForm

5.0.4
-----
- Fix user export celery bug for site

5.0.3
-----
- Add default site to admin users

5.0.2
-----
- Add page_types to security question's model

5.0.1
-----
- Pin molo.core to 5.0.0

5.0.0
-----
- Molo core version 5 support
- Link users to Site
- Add multisite functionality to user profiles

3.2.1
-----
- Add version number

3.2.0
-----
- Add a success page after user log in

3.1.1
-----
- Bug fixing on registration done page

3.1.0
-----
- Add additional fields for registration
- Display Name
- Gender
- Date of birth
- Location
- Education level

3.0.0
-----
- Add terms and conditions on registration

2.2.1
-----
- Updated minimum molo core dependency to 4.3.2

2.2.0
-----
- Ensure that security question index page cannot be deleted

2.1.3
-----
- Fix bug that allowed user's mobile number and email to be deleted when updated despite being required fields

2.1.2
-----
- Use better python logic in forms

2.1.1
-----
- Fixed bug forcing users to add mobile number when not required

2.1.0
-----
- Update template to only show mobile number field if it's activated and has country calling code
- Show a warning message on CMS if mobile number is activated but country calling code has not been set

2.0.2
-----
- Added missing button class for templates

2.0.1
-----
- Updated templates in order to reflect styling changes in modeladmin

2.0.0
-----
- Removed dependency on wagtailmodeladmin

Backwards incompatible changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- Removed use of ``wagtailmodeladmin``: use ``wagtail.contrib.modeladmin`` instead
- ``{% load wagtailmodeladmin_tags %}`` has been replaced by ``{% load modeladmin_tags %}``

NOTE: This release is not compatible with molo versions that are less than 4.0

1.5.1
-----
- Fix duplicated users via wagtail admin

1.5.0
-----
- email CSV

1.4.0
-----
- enable admin to input country code via wagtail

1.3.5
-----
- ensure migration doesn't fail if indexpage already exists

1.3.4
-----
- Allow download as csv for admin users only

1.3.3
-----
- HTML templates Bem class names to reinforce modularity

1.3.2
-----
- Return random subset of security questions for password recovery

1.3.1
-----
- Fix error relating to non-existing questions on Registration Form

1.3.0
-----
- Added password recovery functionality
- Added security questions for password recovery

1.2.6
-----
- Updated change password error messages

1.2.5
-----
- Assigned label to view profile template

1.2.4
-----
- Added BEM class rules to Viewprofiles template

1.2.3
-----
- Added encoding to username when downloading CSV

1.2.2
-----
- Make sure we only encode for users that have alias

1.2.1
-----
- Added encoding to user alias when downloading CSV

1.2.0
-----
- Added End Users view to Wagtail Admin

1.1.0
-----
- Adding BEM rules to the templates

1.0.1
-----
- Removed clean method from EditProfileForm

1.0.0
-----
- Added email address to registration
- Upgraded to Molo 3.0
- Upgraded to Django 1.9

NOTICE:
~~~~~~~
- Not compatible with `molo<3.0`


0.2.7
-----
- Fixed bug in slack stats integration

0.2.6
-----
- Added the option of exporting user data as CSV in django admin

0.2.5
-----
- Added cellphone number to registration
- Added User Profiles Settings in wagtail

0.2.4
-----
- Removed requirement for date of birth when editing profile

0.2.2
-----
- Add missing migrations

0.2.1
-----
- Updated celery task and readme for posting user statistics to a Slack Channel

0.2.0
-----
- Added a task to post user statistics to a Slack Channel
