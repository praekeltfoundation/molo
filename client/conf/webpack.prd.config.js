import webpack from 'webpack';
import base from './webpack.base.config';
import extend from 'lodash/extend';
const UglifyJsPlugin = webpack.optimize.UglifyJsPlugin;


let conf = base('production');


export default extend(conf, {
  plugins: conf.plugins.concat(new UglifyJsPlugin({output: {comments: false}}))
});
