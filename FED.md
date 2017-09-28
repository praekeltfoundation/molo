FED

RESPONSIVE TABLES

$breakpoint-apha: 480px;
.table-class {
  margin: 1em 0;
  min-width: 300px; //To be adjusted

  tr {
    border-top: 1px solid #ddd;
    border-bottom: 1px solid #ddd;
  }

  td {
    visibility: hidden;
  }

  td {
    display: block;
    &:first-child {
      padding-top: .5em;
    }
    &:last-child {
      padding-bottom: .5em;
    }
    &:before {
      content attr(data-th)":";
      font-weight: bold;
      width: 6.5em;
      display: inline-block;
      @media (min-width $breakpoint-apha) {
        display: none;
      }
    }
  }
  th, td {
    align:left;
      @media (min-width $breakpoint-apha) {
        display table-cell;
        padding: .25em .5em;
        &first-child {
          padding-left: 0;
        }

        &:last-child {
          padding-right: 0;
        }
      }
  }

}


TestApp setup
----------------
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
---------------
FED

  Maintenance, Performance, and Readability.

  MARKUP & CSS
  ---------------
  -  We use SMACSS, BEM methodologies

  BEM

  strictbem
  https://en.bem.info/methodology/quick-start/

  hyphenatedbem
  https://csswizardry.com/2013/01/mindbemding-getting-your-head-round-bem-syntax/


  http://getbem.com/introduction/

  BEM Naming Convention
    Languages
    Language__current
    Language__title
    Language__title--icon
    Language__dropdown-button

    Language__list
    Language-list__toggle
    Language-list__item

  SMACSS
  https://smacss.com/book/
  https://webuild.envato.com/blog/how-to-scale-and-maintain-legacy-css-with-sass-and-smacss/

  E.G. variables / colors.scss
    $de_york - #2A9B58;
    $robin_egg_blue - #37BFBE;
    $mandy - #EC3B3A;
    $danube - #5F7AC9;
    $roman - #EF9955;
    $saffron - #F2B438;
    $medium_violet - #B62A99;

  FILE PATH: /styles/core-style/
    /layout/
      _l-header.scss
      _l-footer.scss
      _l-layout.scss | @import all layout compoments
    /modules
      _m-article-list.scss
      _m-article.scss
      _m-modules.scss | @import all modules compoments
    /state
      _s-article-list.scss
      _s-article.scss
      _s-state.scss | @import all state compoments
    /variables
      variables.scss
      color.scss
    _base.scss
    _versions.scss
    styles.scss | @import all compoments
    styles-rtl.scss

  OUTPUT FILE PATH: /static/css/dev with sourcemaps /maps
                    /static/css/prd

  Linting - Enforce editor configs and coding standard rules
  # EditorConfig: http://EditorConfig.org
  Sass Lint
  https://www.npmjs.com/package/sass-lint
  http://sasstools.github.io/make-sass-lint-config/
  https://github.com/sasstools/sass-lint/blob/master/docs/rules/class-name-format.md

  CSS / BEM Linting
  https://github.com/postcss/postcss-bem-linter
  https://github.com/simonsmith/stylelint-selector-bem-pattern

  TESTING
  ------------
  Map out your scraper website workflow 
  https://github.com/segmentio/nightmare
  https://segment.com/blog/ui-testing-with-nightmare/

  COMPRESSION / AUTOMATION
  -------------------------
  Requirements:
  Must have node.js npm and gulp installed globally

  - npm install gulp-cli -g

  For asset bundling & processing, concatenating and minification file:
  - gulpfile.js
  - package.json

  Commands:
  - npm install
  - gulp

  IMAGES FORMATS:
    SVG, PNG, Sprites icons
    Images must be compressed
