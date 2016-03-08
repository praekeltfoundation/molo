import webpack from 'webpack';
import base from './webpack.base.config';
import extend from 'lodash/extend';


export default extend(base(), {
  plugins: [
    new webpack.optimize.UglifyJsPlugin({output: {comments: false}})
  ]
});
