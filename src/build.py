"""Builds the offline iPhone app (index.html + sw.js + manifest + icons) from src/app.html."""
import hashlib, json, os
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.dirname(HERE)
frag = open(os.path.join(HERE, "app.html"), encoding="utf-8").read()
ver = hashlib.sha1(frag.encode()).hexdigest()[:8]
head = """<!doctype html>
<html lang="ru"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Гриф">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="theme-color" content="#eceff3" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0e1115" media="(prefers-color-scheme: dark)">
<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="icon-180.png">
<style>:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>
</head><body>
"""
tail = """
<script>
if ("serviceWorker" in navigator) navigator.serviceWorker.register("sw.js").catch(function(){});
</script>
</body></html>
"""
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(head + frag + tail)
open(os.path.join(OUT, "sw.js"), "w").write("""// Гриф: офлайн-кэш. Версия меняется при каждой сборке.
const CACHE = "grif-%s";
const FILES = ["./", "index.html", "manifest.webmanifest", "icon-180.png", "icon-512.png"];
self.addEventListener("install", e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)).then(() => self.skipWaiting())); });
self.addEventListener("activate", e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener("fetch", e => {
  if (e.request.method !== "GET" || new URL(e.request.url).origin !== location.origin) return;
  // Сначала кэш (работает в море), в фоне обновляем, если есть интернет.
  e.respondWith(caches.match(e.request, {ignoreSearch: true}).then(hit => {
    const net = fetch(e.request).then(r => { if (r && r.ok && new URL(e.request.url).origin === location.origin) caches.open(CACHE).then(c => c.put(e.request, r.clone())); return r; }).catch(() => hit);
    return hit || net;
  }));
});
""" % ver)
json.dump({"name":"Гриф — журнал тренировок","short_name":"Гриф","start_url":"./","scope":"./","display":"standalone",
           "background_color":"#eceff3","theme_color":"#1d4fd0","lang":"ru",
           "icons":[{"src":"icon-180.png","sizes":"180x180","type":"image/png"},{"src":"icon-512.png","sizes":"512x512","type":"image/png","purpose":"any maskable"}]},
          open(os.path.join(OUT, "manifest.webmanifest"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
def icon(n):
    s = 4; N = n*s; im = Image.new("RGB", (N, N), "#1d4fd0"); d = ImageDraw.Draw(im)
    c = N/2; bar_h = N*0.07
    d.rounded_rectangle([N*0.08, c-bar_h/2, N*0.92, c+bar_h/2], radius=bar_h/2, fill="#e8ebf0")
    for x, h, w, col in [(0.22,0.50,0.09,"#cf3626"),(0.31,0.38,0.06,"#f0c22c"),(0.69,0.38,0.06,"#f0c22c"),(0.78,0.50,0.09,"#cf3626")]:
        d.rounded_rectangle([N*x-N*w/2, c-N*h/2, N*x+N*w/2, c+N*h/2], radius=N*0.02, fill=col)
    im.resize((n, n), Image.LANCZOS).save(os.path.join(OUT, f"icon-{n}.png"))
icon(180); icon(512)
print("built", ver)
