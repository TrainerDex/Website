const path = require('path');

module.exports = {
  entry: './assets/src/js/index.js',
  output: {
    filename: 'index-bundle.js',
    path: path.resolve(__dirname, './assets/build/js'),
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        loader: "babel-loader",
        options: { presets: ["@babel/preset-env", "@babel/preset-react"] }
      },
    ]
  }
};
