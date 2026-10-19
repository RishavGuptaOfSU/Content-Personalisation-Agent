import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'node:path'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  // Phase 2 runs on its own ports so it can sit alongside phase-1 (8000/5173).
  const apiTarget = env.BACKEND_ORIGIN || 'http://localhost:8010'

  return {
    plugins: [react()],
    resolve: {
      alias: { '@': path.resolve(import.meta.dirname, 'src') },
    },
    server: {
      port: Number(env.FRONTEND_PORT || 5174),
      host: true,
      strictPort: false,
      // Lets the app work with VITE_API_BASE_URL=/api (same-origin, no CORS).
      proxy: {
        '/api': { target: apiTarget, changeOrigin: true },
        '/health': { target: apiTarget, changeOrigin: true },
      },
    },
    preview: { port: 4173 },
    build: { outDir: 'dist', sourcemap: mode !== 'production' },
  }
})
