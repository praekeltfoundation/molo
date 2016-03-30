import replay from 'replay';
import jsdom from 'jsdom';
import { join } from 'path';
import conf from 'src/conf';


global.document = jsdom.jsdom('<!doctype html><html><body></body></html>');
global.window = document.defaultView;
global.navigator = {userAgent: 'node.js'};


replay.reset('localhost');
replay.fixtures = join(__dirname, '.http-fixtures');


conf.apiPrefix = 'http://localhost:8000';
conf.csrfToken = 'ZC4jl7ZzhT3ufnJsEqlCwZJ5mCowUeJh';
conf.apiHeaders.Cookie = [
    'csrftoken=ZC4jl7ZzhT3ufnJsEqlCwZJ5mCowUeJh',
    'sessionid=r6v7pgp38joi5wgujk7vzanm5mwlitu1'
  ]
  .join('; ');
