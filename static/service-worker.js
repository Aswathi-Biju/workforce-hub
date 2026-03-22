const CACHE_NAME = 'workforce-hub-v1';
const urlsToCache = [
  '/',
  '/static/css/custom.css',
  '/static/js/main.js',
  '/static/manifest.json'
];

// Install service worker
self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME).then(function(cache) {
      return cache.addAll(urlsToCache);
    })
  );
});

// Fetch from cache
self.addEventListener('fetch', function(event) {
  event.respondWith(
    caches.match(event.request).then(function(response) {
      if (response) {
        return response;
      }
      return fetch(event.request);
    })
  );
});