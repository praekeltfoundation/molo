import webpack from 'webpack';
import { resolve } from 'path';
import mapValues from 'lodash/mapValues';


const DefinePlugin = webpack.DefinePlugin;
const CommonsChunkPlugin = webpack.optimize.CommonsChunkPlugin;


export default function base(env) {
  // TODO extend wagtail's bundling process when this is supported
  // github.com/torchbox/wagtail/issues/2315

  return {
    entry: {
      'git-import': './src/views/git-importer/entry',
    },
    resolve: {
      root: resolve(__dirname, '..')
    },
    output: {
      filename: '[name].js'
    },
    plugins: [
      new CommonsChunkPlugin('commons.js'),
      new DefinePlugin(mapValues({
        'process.env.NODE_ENV': env
      }, JSON.stringify))
    ],
    module: {
      loaders: [{
        test: /\.js$/,
        loader: 'babel',
        include: [
          resolve(__dirname, '..', 'src'),
          resolve(__dirname, '..', 'tests')
        ]
      }]
    }
  };
}
