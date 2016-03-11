import webpack from 'webpack';
const CommonsChunkPlugin = webpack.optimize.CommonsChunkPlugin;


export default function base() {
  // TODO extend wagtail's bundling process when this is supported
  // github.com/torchbox/wagtail/issues/2315

  return {
    entry: {
      'git-import': './src/views/git-importer/entry'
    },
    output: {
      filename: '[name].js'
    },
    plugins: [
      new CommonsChunkPlugin('commons.js')
    ],
    module: {
      loaders: [{
        test: /\.js$/,
        loader: 'babel'
      }]
    }
  };
}
