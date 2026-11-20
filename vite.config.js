import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Emits a service worker that precaches every built file so the app opens offline after the first visit.
const offlineSW = () => ({
  name: 'hali-offline-sw',
  apply: 'build',
  generateBundle(_, bundle) {
    const files = ['./', 'manifest.webmanifest', 'icon.svg', 'icon-192.png', 'icon-512.png', ...Object.keys(bundle)]
    this.emitFile({ type: 'asset', fileName: 'sw.js', source: `const V='hali-${Date.now()}';const FILES=${JSON.stringify(files)};
self.addEventListener('install',e=>{e.waitUntil(caches.open(V).then(c=>Promise.all(FILES.map(f=>c.add(f).catch(()=>{})))).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==V).map(x=>caches.delete(x)))).then(()=>self.clients.claim()))});
self.addEventListener('fetch',e=>{if(e.request.method!=='GET')return;const u=new URL(e.request.url);if(u.origin!==self.location.origin||u.pathname==='/api'||u.pathname.startsWith('/api/'))return;e.respondWith(caches.match(e.request,{ignoreSearch:true}).then(m=>m||fetch(e.request).then(r=>{const c=r.clone();caches.open(V).then(x=>x.put(e.request,c));return r}).catch(()=>caches.match('./'))))});` })
  },
})

export default defineConfig({
  plugins: [react(), offlineSW()],
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:8001',
    },
  },
  build: { rollupOptions: { output: { manualChunks: { vendor: ['react', 'react-dom', 'react-router-dom'], charts: ['recharts'] } } } },
})
