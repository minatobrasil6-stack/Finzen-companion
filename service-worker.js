// Cachea el "shell" (este HTML + manifest + ícono) para que la app abra rápido
// e incluso muestre algo si no hay internet un instante. El CONTENIDO de
// FinZen (dentro del iframe) sigue necesitando conexión real, porque
// Streamlit necesita una conexión activa al servidor para funcionar.
const CACHE_NAME = "finzen-shell-v1";
const ARCHIVOS_SHELL = ["./", "./index.html", "./manifest.json", "./icon.png"];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(ARCHIVOS_SHELL)));
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(clients.claim());
});

self.addEventListener("fetch", (event) => {
  // Solo cachea el shell -- todo lo que vaya hacia el iframe de Streamlit
  // (otro origen) pasa directo, sin interferir con su propia conexión.
  const url = new URL(event.request.url);
  if (url.origin === self.location.origin) {
    event.respondWith(
      caches.match(event.request).then((cached) => cached || fetch(event.request))
    );
  }
});
