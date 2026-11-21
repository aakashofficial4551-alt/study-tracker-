const CACHE_NAME = "studyos-v1";
const STATIC_ASSETS = [
  "/manifest.json",
  "/static/icons/icon-192.png",
  "/static/icons/icon-512.png"
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") return;

  event.respondWith(
    fetch(event.request)
      .then((response) => {
        if (response && response.status === 200 && event.request.url.includes("/static/")) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
        }
        return response;
      })
      .catch(() =>
        caches.match(event.request).then((cached) => {
          if (cached) return cached;
          return new Response(
            "<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>Offline - StudyOS</title><style>body{background:#07070a;color:#f8fafc;font-family:sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;margin:0;text-align:center;padding:20px;}button{margin-top:16px;padding:12px 22px;border:none;border-radius:10px;background:#ff2a85;color:#fff;font-weight:700;font-size:15px;}</style></head><body><div><h2>No Internet Connection</h2><p style='color:#94a3b8;'>Connect to the internet to sync your StudyOS records.</p><button onclick='location.reload()'>Retry</button></div></body></html>",
            { headers: { "Content-Type": "text/html" } }
          );
        })
      )
  );
});
