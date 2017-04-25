FED
TestApp setup
MOLO CORE TEMPLATES - USES DEFAULT PATTERNS
  DO NOT CHANGE THOSE DUE TO TESTS 

$ virtualenv ve
$ source ve/bin/activate
(ve)$ pip install -e .

$ molo scaffold testapp
$ cd testapp
$ ./manage.py migrate
$ ./manage.py createsuperuser
$ ./manage.py runserver

Celery Worker
$ ./manage.py celery worker -A testapp -l INFO
$ ./manage.py celery beat -l INFO -A testapp


MARKUP & CSS
-  We use SMACSS, BEM methodologies
SMACSS Structure
https://smacss.com/book/

BEM
https://en.bem.info/methodology/quick-start/
http://getbem.com/introduction/

CSS / BEM Linting
https://github.com/postcss/postcss-bem-linter
- Enforce coding standard rules


COMPRESSION / AUTOMATION

Node / NPM
- Gulp module
  - For asset bundling & processing, concatenating and minification
    gulpfile.js
    package.json
Commands:
- npm install
- npm run build

IMAGES
  Image formats:
  SVG, PNG, Sprites icons
  Image compression
