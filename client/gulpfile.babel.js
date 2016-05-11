import gulp from 'gulp';
import defaults from 'lodash/defaults';
import plumber from 'gulp-plumber';
import webpack from 'webpack-stream';
import jscs from 'gulp-jscs';
import jshint from 'gulp-jshint';
import mocha from 'gulp-mocha';
import sass from 'gulp-sass';
import rename from 'gulp-rename';
import gutil from 'gulp-util';
import { JSXHINT as linter } from 'jshint-jsx';

import webpackPrd from './conf/webpack.prd.config';
import webpackDev from './conf/webpack.dev.config';
import sassPrd from './conf/sass.prd.config';
import sassDev from './conf/sass.dev.config';


const env = process.env.NODE_ENV || 'development';


const webpackConf = {
  'development': webpackDev,
  'production': webpackPrd
}[env];


const sassConf = {
  'development': sassDev,
  'production': sassPrd
}[env];


const paths = {
  conf: [
    'gulpfile.babel.js',
    'conf/**/*.js'
  ],
  scripts: [
    'src/**/*.js'
  ],
  tests: [
    'tests/**/*.js'
  ],
  styles: [
    'src/**/*.scss'
  ],
  dest: '../molo/core/static'
};


gulp.task('build:scripts', () => {
  return webpack(webpackConf)
    .pipe(gulp.dest(`${paths.dest}/js`));
});


gulp.task('build:styles', () => {
  return gulp.src('./src/styles/index.scss')
    .pipe(plumber(err))
    .pipe(sass(sassConf))
    .pipe(rename('molo.css'))
    .pipe(gulp.dest(`${paths.dest}/css`));
});


gulp.task('watch:scripts', () => {
  return webpack(defaults(webpackConf, {
    watch: true,
    keepalive: true
  }));
});


gulp.task('lint:conf', () => lint(paths.conf));
gulp.task('lint:scripts', () => lint(paths.scripts));
gulp.task('lint:tests', () => lint(paths.tests));


gulp.task('test', () => {
  return gulp.src(paths.tests)
  .pipe(mocha({
    require: ['./tests/setup.js'],
    timeout: process.env.TIMEOUT || 2000
  }));
});


gulp.task('watch', () => {
  gulp.watch(paths.conf, ['lint:conf']);
  gulp.watch(paths.styles, ['build:styles']);

  gulp.watch(
    paths.scripts.concat(paths.tests),
    ['lint:scripts', 'lint:tests', 'build:scripts', 'test']);
});


function lint(paths) {
  return gulp.src(paths)
    .pipe(plumber(err))
    .pipe(jscs())
    .pipe(jshint({linter: linter}))
    .pipe(jshint.reporter('jshint-stylish'));
}


function err(e) {
  gutil.log(e.message);
  this.emit('end');
}


gulp.task('lint', ['lint:conf', 'lint:scripts', 'lint:tests']);
gulp.task('build', ['build:scripts', 'build:styles']);
gulp.task('ci', ['lint', 'build', 'test']);
gulp.task('default', ['build', 'test']);
