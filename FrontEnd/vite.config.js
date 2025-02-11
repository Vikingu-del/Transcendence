import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';

export default defineConfig({
  plugins: [vue()],
  build: {
    sourcemap: true,
    rollupOptions: {
      output: {
        sourcemapExcludeSources: true,
      }
    }
  },
  optimizeDeps: {
    exclude: ['vue', 'vuex', 'vue-router'],
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  server: {
    host: '0.0.0.0', // Used to be host: true which only allows localhost access but 0.0.0.0 allows connections from any IP address
    port: 5173, 
    watch: {
      usePolling: true
    },
    proxy: {
      '/api': {
        target: 'http://user:8000', // Used to be 'http://localhost:8000' which allows access only from container but http://user:8000 Uses Docker service name, accessible across containers
        changeOrigin: true,
        // rewrite: (path) => path.replace(/^\/api/, '') Since the backend URLs already include /api/ prefix: Removed the rewrite rule:
      },
      '/vault': {
        target: 'http://localhost:8200',
        changeOrigin: true,
      },
    }
  }
});
