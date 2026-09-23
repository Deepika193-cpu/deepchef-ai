import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
  preview: {
    // Mirrors the dev proxy so `vite preview` (used by the Docker frontend
    // container) also forwards /api calls — points at the `backend` service
    // name, which only resolves inside the docker-compose network.
    proxy: {
      '/api': process.env.VITE_API_PROXY_TARGET || 'http://backend:8000',
    },
  },
});
