const config = require('./config');

module.exports = {
  devServer: {
    proxy: {
      '/api': {
        target: config.API_SERVER,
        changeOrigin: true,
        secure: false
      }
    }
  }
}
