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


const env = process.env.NODE_ENV || 'dev';


const webpackConf = {
  'dev': webpackDev,
  'prd': webpackPrd
}[env];


const sassConf = {
  'dev': sassDev,
  'prd': sassPrd
}[env];


const paths = {
  conf: [
    'gulpfile.babel.js',
    'conf/**/*.js'
  ],
  scripts: [
    'src/**/*.js'
  ],
  styles: [
    'src/**/*.scss'
  ]
};


gulp.task('build:scripts', () => {
  return webpack(webpackConf)
    .pipe(gulp.dest('./dist/js'));
});


gulp.task('build:styles', () => {
  return gulp.src('./src/styles/index.scss')
    .pipe(plumber(err))
    .pipe(sass(sassConf))
    .pipe(rename('molo.css'))
    .pipe(gulp.dest('./dist/css'));
});


gulp.task('watch:scripts', () => {
  return webpack(defaults(webpackConf, {
    watch: true,
    keepalive: true
  }));
});


gulp.task('lint:conf', () => lint(paths.conf));
gulp.task('lint:scripts', () => lint(paths.scripts));


gulp.task('test', () => {
  return gulp.src(['./tests/**/*.test.js'])
    .pipe(mocha({require: ['./tests/setup.js']}));
});


gulp.task('watch', () => {
  gulp.watch(paths.conf, ['lint']);
  gulp.watch(paths.scripts, ['lint', 'build:scripts', 'test']);
  gulp.watch(paths.styles, ['build:styles']);
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


gulp.task('lint', ['lint:conf', 'lint:scripts']);
gulp.task('build', ['build:scripts', 'build:styles']);
gulp.task('ci', ['lint', 'build', 'test']);
gulp.task('default', ['build', 'test']);
