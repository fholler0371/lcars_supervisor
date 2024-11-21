let CACHE_VERSION = 2;
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
    '/js_lib/jqwidgets/jqxwindow.js',
    '/js_lib/jqwidgets/jqxscrollbar.js',
    '/js_lib/jqwidgets/jqxlistbox.js',
    '/js_lib/jqwidgets/jqxdropdownlist.js',
    '/js_lib/jqwidgets/jqxsplitter.js',
    '/js_lib/jqwidgets/jqxcheckbox.js',
    '/js_lib/jqwidgets/jqxnumberinput.js',
    'js_lib/jqwidgets/jqxdata.js',
    'js_lib/jqwidgets/jqxgrid.js',
    'js_lib/jqwidgets/jqxgrid.selection.js',
    '/js_lib/packery.js',
    '/js_lib/qrcode.min.js',
    '/js/mod/app.js',
    // auth
    '/auth/js/mod/auth_user.js',
    '/auth/js/mod/auth_user_sec.js',
    // budget
    'budget/js/mod/budget_overview.js',
    'budget/js/mod/budget_cat.js'
  ],
  image : [
    '/img/mdi/home.svg',
    '/img/mdi/fullscreen.svg',
    '/img/mdi/login.svg',
    '/img/mdi/logout.svg',
    '/img/mdi/account.svg',
    'img/mdi/account-lock.svg', 
    '/img/mdi/router-wireless.svg',
    '/img/mdi/menu.svg',
    '/img/mdi/clock.svg',
    '/img/mdi/cog-outline.svg',
    '/img/mdi/refresh.svg',
    '/img/mdi/information-box-outline.svg',
    '/img/mdi/cash-multiple.svg',
    'img/mdi/information-variant.svg',
    '/js_lib/jqwidgets/styles/images/error.png',
    '/js_lib/jqwidgets/styles/images/info.png',
    '/js_lib/jqwidgets/styles/images/close_white.png',
    '/js_lib/jqwidgets/styles/images/close.png',
    '/js_lib/jqwidgets/styles/images/material-icon-down-white.png',
    '/js_lib/jqwidgets/styles/images/material-icon-up-white.png',
    '/js_lib/jqwidgets/styles/images/material-icon-left.png',
    '/js_lib/jqwidgets/styles/images/material-icon-right.png',
//    '/js_lib/jqwidgets/styles/images/loader.js',
    '/css/images/finance.svg',
    '/css/images/katalog.svg',
    'css/images/cash.svg',
    '/css/images/material_check_white.png'
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
          let entry = ASSETS[key][i]
          caches.match(entry).then(cacheRes => {
            if (cacheRes == undefined) {
              cache.add(entry)
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
        if (!(ev.request.method == 'POST')) {
          console.log('Fehlt in Cache: '+ev.request.url, ev.request.method)
        }
      }
      return cacheRes || fetch(ev.request)
    })
  )
})

