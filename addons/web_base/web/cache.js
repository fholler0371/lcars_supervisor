/*
 Copyright 2014 Google Inc. All Rights Reserved.
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at
 http://www.apache.org/licenses/LICENSE-2.0
 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
*/

let CACHE_VERSION = 1;
let CURRENT_CACHES = {
  font: 'cache-v' + CACHE_VERSION
}
let BLOCK = [
  '/main.js',
  'libary_definitions.js',
  '_dev.js'
]

self.addEventListener('activate', function(event) {
  var expectedCacheNamesSet = new Set(Object.values(CURRENT_CACHES));
  event.waitUntil(
    caches.keys().then(function(cacheNames) {
      return Promise.all(
        cacheNames.map(function(cacheName) {
          if (!expectedCacheNamesSet.has(cacheName)) {
            // If this cache name isn't present in the set of "expected" cache names, then delete it.
            //console.log('Deleting out of date cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

self.addEventListener('fetch', function(event) {
  console.log('Handling fetch event for', event.request.url);

  event.respondWith(
    caches.open(CURRENT_CACHES.font).then(function(cache) {
      return cache.match(event.request).then(function(response) {
        if (response) {
          //console.log(' Found response in cache:', response);
          var allowed = true
          BLOCK.forEach(function(item) {
            if (event.request.url.includes(item)) {
              allowed = false
            }
          })
          if (allowed) {
            return response;
          }
        }
        return fetch(event.request.clone()).then(function(response) {
          if (event.request.method == "GET") {
            if (!event.request.url.includes('?') && event.request.url.includes('https')) {
              var allowed = true
              BLOCK.forEach(function(item) {
                if (event.request.url.includes(item)) {
                  allowed = false
                }
              })
              if (allowed) {
                cache.put(event.request, response.clone())
              }
            }  
          }
          return response;
        });
      }).catch(function(error) {
        console.error('  Error in fetch handler:', error);

        throw error;
      });
    })
  );
});