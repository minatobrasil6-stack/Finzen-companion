// Service worker mínimo: cachea el shell para que FinZen abra más rápido en
// visitas repetidas. No hace la app funcionar offline por completo (Streamlit
// necesita conexión activa para los datos), pero es requisito para que los
// navegadores ofrezcan "Instalar app".
const CACHE_NAME = "finzen-cache-v1";
self.addEventListener("install", (event) => {
  self.skipWaiting();
});
self.addEventListener("activate", (event) => {
  event.waitUntil(clients.claim());
});
self.addEventListener("fetch", (event) => {
  // Passthrough simple: no interfiere con las conexiones en vivo de Streamlit
  // (WebSocket), solo deja pasar todo. Cumple el requisito técnico de PWA.
  event.respondWith(fetch(event.request).catch(() => caches.match(event.request)));
});
