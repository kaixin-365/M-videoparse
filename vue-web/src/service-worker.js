// 设置相应缓存的名字的前缀和后缀
workbox.core.setCacheNameDetails({
    prefix: 'video-link-cache',
    suffix: 'v2022.06.30',
})
// 让我们的service worker尽快的得到更新和获取页面的控制权
workbox.core.skipWaiting();
workbox.core.clientsClaim();
 
/* vue-cli3.0通过workbox-webpack-plagin 来实现相关功能，我们需要加入
* 以下语句来获取预缓存列表和预缓存他们，也就是打包项目后生产的html，js，css等\* 静态文件
*/
workbox.precaching.precacheAndRoute(self.__precacheManifest || []);
// 缓存web的css资源
workbox.routing.registerRoute(
    // Cache CSS files
    /.*\.css/,
    // 使用缓存，但尽快在后台更新
    workbox.strategies.staleWhileRevalidate({
        // 使用自定义缓存名称
        cacheName: 'css-cache'
    })
);
 
// 缓存web的js资源
workbox.routing.registerRoute(
    // 缓存JS文件
    /.*\.js/,
    // 使用缓存，但尽快在后台更新
    workbox.strategies.staleWhileRevalidate({
        // 使用自定义缓存名称
        cacheName: 'js-cache'
    })
);
 
// 缓存web的图片资源
workbox.routing.registerRoute(
    /\.(?:png|gif|jpg|jpeg|svg)$/,
    // 使用缓存，但尽快在后台更新
    workbox.strategies.staleWhileRevalidate({
        // 使用自定义缓存名称
        cacheName: 'images'
    })
);