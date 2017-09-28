'use strict';

var gulp              =   require('gulp'),
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
    sassPaths = [
        'molo/core/styles/core-style/styles.s+(a|c)ss',
        'molo/core/styles/mote/mote.s+(a|c)ss'
    ],
    sassDest = {
         prd: 'molo/core/static/css/prd',
         dev: 'molo/core/static/css/dev'
    };

function styles(env) {
  var s = gulp.src(sassPaths);
  var isDev = env === 'dev';
  console.log("argv env param:",isDev);
  if (isDev)
    s = s
      .pipe(sourcemaps.init());
    s = s
    .pipe(sass().on('error', sass.logError))
    .pipe(sassGlob())
    .pipe(bless())
    .pipe(cleanCSSMinify())
    //.pipe(sassLint())
    //.pipe(sassLint.format())
    //.pipe(sassLint.failOnError())
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
  gulp.src('molo/core/styles/wagtail-admin.scss')
      .pipe(sass().on('error', sass.logError))
      .pipe(sassGlob())
      .pipe(cleanCSSMinify())
      .pipe(gulp.dest('molo/core/static/css/'))
      .pipe(notify({ message: 'Styles task complete: Wagtail Admin' }));
});

gulp.task('watch', function() {
    livereload.listen();
    gulp.watch(['molo/styles/**/*.scss'],['styles']);
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

gulp.task('styles', ['styles:dev', 'styles:prd','stylesAdmin']);
gulp.task('default', ['styles', 'compress']);
