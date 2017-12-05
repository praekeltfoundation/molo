'use strict';

var gulp              =   require('gulp'),
    glob              =   require('glob'),
    sass              =   require('gulp-sass'),
    sassLint          =   require('gulp-sass-lint'),
    sassGlob          =   require('gulp-sass-glob'),
    cleanCSSMinify    =   require('gulp-clean-css'),
    autoprefixer      =   require('gulp-autoprefixer'),
    bless             =   require('gulp-bless'),
    watch             =   require('gulp-watch'),
    rename            =   require('gulp-rename'),
    gzip              =   require('gulp-gzip'),
    notify            =   require('gulp-notify'),
    sourcemaps        =   require('gulp-sourcemaps'),
    livereload        =   require('gulp-livereload'),
    minify            =   require('gulp-minify'),
    pixrem            =   require('gulp-pixrem'),
    svgmin            =   require('gulp-svgmin'),
    del               =   require('del'),

    sassPaths = [
        'molo/core/styles/sass/styles.s+(a|c)ss',
        'molo/core/styles/mote.customize/mote.s+(a|c)ss'
    ],
    sassDest = {
         prd: 'molo/core/static/css/prd',
         dev: 'molo/core/static/css/dev'
    },
    iconsPath = 'molo/core/static/images',
    iconsDest = 'molo/core/static/images/generated-icons';

function styles(env) {
  var s = gulp.src(sassPaths);
  var isDev = env === 'dev';
  if (isDev)
    s = s
      .pipe(sourcemaps.init());
    s = s
    .pipe(sassGlob())
    .pipe(sass().on('error', sass.logError))
    .pipe(bless())
    .pipe(cleanCSSMinify())
    .pipe(autoprefixer({
        browsers: [
            'ie >= 8',
            'android >= 2.3',
            'iOS >= 6',
            '> 0%'
        ]
    }))
    .pipe(pixrem());
    if (isDev)
    s = s
      .pipe(sourcemaps.write('/maps'));
    return s
    .pipe(gulp.dest(sassDest[env]))
    .pipe(notify({ message: `Styles task complete: ${env}` }));
}
gulp.task('styles:prd', function() {
  return styles('prd');
});
gulp.task('styles:dev', function() {
  return styles('dev');
});

//Wagtail Admin CSS override - must be on root static
gulp.task('stylesAdmin', function() {
  gulp.src('molo/core/styles/wagtail-admin/wagtail-admin.s+(a|c)ss')
      .pipe(sassGlob())
      .pipe(sass().on('error', sass.logError))
      .pipe(cleanCSSMinify())
      .pipe(gulp.dest('molo/core/static/css/'))
      .pipe(notify({ message: 'Styles task complete: Wagtail Admin' }));
});

gulp.task('watch', function() {
    livereload.listen();
    gulp.watch(['molo/core/styles/**/*.scss'],['styles']);
});

// Minify JS
gulp.task('compress', function() {
  gulp.src('molo/core/static/js/molo.js')
    .pipe(minify({
        ext:{
            min:'-min.js'
        },
    }))
    .pipe(gulp.dest('molo/core/static/js/'))
});

//Icons

gulp.task('clean-generated-icons', function() {
    return del(iconsPath + '/svgs');
});
gulp.task('crush-svgs', ['clean-generated-icons'], function () {
    return gulp.src(iconsPath + '/icons/*.svg')
        .pipe(svgmin({
          js2svg: {
                pretty: true
            }
        }))
        .pipe(gulp.dest(iconsPath + '/svgs'));
});
gulp.task('clean-icons', function() {
    return del(iconsDest);
});
gulp.task('icons', ['clean-icons', 'crush-svgs'], function(done) {
    var icons = glob.sync(iconsPath + '/svgs/*.*'); //Get array of files from glob pattern
    var options = {
      enhanceSVG: true,
      dynamicColorOnly: true,
      colors: {
        white: '#ffffff',
        black: '#000000'
      }
    };
});

gulp.task('styles', ['styles:dev', 'styles:prd','stylesAdmin']);
gulp.task('default', ['styles', 'compress']);
