'use strict';

var gulp              =   require('gulp'),
    sass              =   require('gulp-sass'),
    watch             =   require('gulp-watch'),
    cleanCSSMinify    =   require('gulp-clean-css'),
    rename            =   require('gulp-rename'),
    gzip              =   require('gulp-gzip'),
    notify            =   require('gulp-notify'),
    sourcemaps        =   require('gulp-sourcemaps'),
    livereload        =   require('gulp-livereload'),
    minify            =   require('gulp-minify'),
    sassPaths = [
        'molo/core/styles/core-style/styles.scss',
        'molo/core/styles/mote/mote.scss'
    ],
    sassDest = {
         prd: 'molo/core/static/css/prd',
         dev: 'molo/core/static/css/dev'
    };


function styles(env) {
  var s = gulp.src(sassPaths);
  var isDev = env === 'dev';

  if (isDev) s = s
    .pipe(sourcemaps.init());

    s = s
    .pipe(sass().on('error', sass.logError))
    .pipe(cleanCSSMinify())
    if (isDev) s = s
        .pipe(sourcemaps.write('/maps'));
        return s
        .pipe(gulp.dest(sassDest[env]))
        .pipe(notify({ message: `Styles task complete: ${env}` }));
}

//Wagtail Admin CSS override - must be on root static
gulp.task('stylesAdmin', function() {
  gulp.src('molo/core/styles/wagtail-admin.scss')
      .pipe(sass().on('error', sass.logError))
      .pipe(cleanCSSMinify())
      .pipe(gulp.dest('molo/core/static/css/'))
      .pipe(notify({ message: 'Styles task complete: Wagtail Admin' }));
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

gulp.task('styles:prd', function() {
  return styles('prd');
});
gulp.task('styles:dev', function() {
  return styles('dev');
});

gulp.task('watch', function() {
    livereload.listen();
    gulp.watch(['molo/styles/**/*.scss'],['styles']);
});

gulp.task('styles', ['styles:dev', 'styles:prd','stylesAdmin']);
gulp.task('default', ['styles', 'compress','watch']);
