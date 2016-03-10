import base from './webpack.base.config';
import extend from 'lodash/extend';


export default extend(base(), {
  devtool: '#inline-source-map'
});
