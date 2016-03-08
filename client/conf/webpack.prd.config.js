import webpack from 'webpack';
import base from './webpack.base.config';


let config = base();


config.plugins = [
  new webpack.optimize.UglifyJsPlugin({output: {comments: false}})
];


config.output.filename = '[name].min.js';


export default config;
