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
