import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Support an optional VITE_API_URL. If not provided, we proxy /api -> backend (default 5001).
const API_TARGET = process.env.VITE_API_URL || 'http://localhost:5001';

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: API_TARGET,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})
