import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: true,
    allowedHosts: true,
    proxy: {
      '/upload': { target: 'http://localhost:4173', changeOrigin: false },
      '/have-json': { target: 'http://localhost:4173', changeOrigin: false },
      '/have': { target: 'http://localhost:4173', changeOrigin: false },
      '/manifest.json': { target: 'http://localhost:4173', changeOrigin: false },
      '/stats': { target: 'http://localhost:4173', changeOrigin: false },
      '/exporter': { target: 'http://localhost:4173', changeOrigin: false, rewrite: (p) => p.replace(/^\/exporter/, '') },
    },
  },
  build: { outDir: 'dist' },
})
