/*
 * @Author: your name
 * @Date: 2021-02-21 12:31:10
 * @LastEditTime: 2021-02-25 12:52:19
 * @LastEditors: Please set LastEditors
 * @Description: In User Settings Edit
 * @FilePath: \html\vue.config.js
 */

/*  chainWebpack: config => {
    config.plugins.delete('pwa');
    config.plugins.delete('workbox');
  },
*/


module.exports = {
  transpileDependencies: [
    'vuetify'
  ],
  publicPath: './',
  pwa: {
    name: '视频外链',
    themeColor: '#7b7ff7',
    msTileColor: '#000000',
    appleMobileWebAppCapable: 'yes',
    appleMobileWebAppStatusBarStyle: 'black',
    // configure the workbox plugin (GenerateSW or InjectManifest)
    workboxPluginMode: 'InjectManifest',
    workboxOptions: {
        // swSrc is required in InjectManifest mode.
        swSrc: './src/service-worker.js',
    }
  }
}
