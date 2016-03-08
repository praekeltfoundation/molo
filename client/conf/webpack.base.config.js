import { resolve } from 'path';


export default function base() {
  // TODO extend wagtail's bundling process when this is supported
  // github.com/torchbox/wagtail/issues/2315

  return {
    entry: {
      'git-import': './src/entries/git-import'
    },
    output: {
      filename: '[name].js'
    },
    resolve: {
      alias: {
        components: pathTo('src/components')
      }
    },
    module: {
      loaders: [{
        test: /\.js$/,
        loader: 'babel'
      }]
    }
  };
}


function pathTo(pathname) {
  return resolve(__dirname, '..', pathname);
}
