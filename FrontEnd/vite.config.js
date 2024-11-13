import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  proxy: {
    // Proxy all requests to `/user` and other paths to the user service
    '/user': 'http://localhost:8000',
    '/register': 'http://localhost:8000/register/',
    '/login': 'http://localhost:8000/login/',
    '/profile': 'http://localhost:8000/profile/',
    '/logout': 'http://localhost:8000/logout/',
    '/friends': 'http://localhost:8000/friends/',
    '/match-history': 'http://localhost:8000/match-history/',
    '/vault': 'http://localhost:8200',
  }
})
