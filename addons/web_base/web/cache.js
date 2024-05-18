let CACHE_VERSION = 1;
let CURRENT_CACHES = {
  static: 'staticCache-v' + CACHE_VERSION,
  script: 'scriptCache-v' + CACHE_VERSION,
  image: 'imageCache',
  css: 'cssCache',
  font: 'fontCache'
}

let ASSETS = {
  static : [
    '/',
    '/auth/user'
  ],
  script : [
    '/js_lib/require.js',
    '/js_lib/jquery/jquery-3.7.0.js',
    '/js_lib/svg-inject.js',
    '/js_lib/jqwidgets/jqxcore.js',
    '/js_lib/jqwidgets/jqxnotification.js',
    '/js_lib/jqwidgets/jqxinput.js',
    '/js_lib/jqwidgets/jqxpasswordinput.js',
    '/js_lib/jqwidgets/jqxbuttons.js',
    '/js_lib/packery.js',
    '/js/mod/app.js'
  ],
  image : [
    '/img/mdi/home.svg',
    '/img/mdi/fullscreen.svg',
    '/img/mdi/login.svg',
    '/img/mdi/logout.svg',
    '/img/mdi/account.svg',
    '/img/mdi/menu.svg',
    '/img/mdi/clock.svg'
  ],
  css : [
    '/js_lib/jqwidgets/styles/jqx.base.css',
    '/css/core.css',
    '/css/jqx.material.css'
  ],
  font : [
    '/css/lcars.ttf'
  ]
}
let staticAssets = 

self.addEventListener('install', function(ev) {
  //console.log('SW installed')
  for (const [key, value] of Object.entries(CURRENT_CACHES)) {
    ev.waitUntil( 
      caches.open(CURRENT_CACHES[key]).then(cache=>{
        for (i in ASSETS[key]) {
          caches.match(ASSETS[key][i]).then(cacheRes => {
            if (cacheRes == undefined) {
              cache.add(ASSETS[key][i])
            } 
          })
        }
      })
    )
  }
  self.skipWaiting()
})

self.addEventListener('activate', function(ev) {
  var expectedCacheNamesSet = new Set(Object.values(CURRENT_CACHES))
  ev.waitUntil(
    caches.keys().then(function(cacheNames) {
      return Promise.all(
        cacheNames.map(function(cacheName) {
          if (!expectedCacheNamesSet.has(cacheName)) {
            // If this cache name isn't present in the set of "expected" cache names, then delete it.
            //console.log('Deleting out of date cache:', cacheName);
            return caches.delete(cacheName)
          }
        })
      )
    })
  )
})

self.addEventListener('fetch', function(ev) {
  //console.log('fetch request for', ev.request.url)
  ev.respondWith(
    caches.match(ev.request).then(cacheRes => {
      if (cacheRes == undefined) {
        console.log('Fehlt in Cache: '+ev.request.url)
      }
      return cacheRes || fetch(ev.request)
    })
  )
})

