import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { readFileSync } from 'node:fs'

// The app version lives in ../app_version.py; read it so the UI never drifts.
const appVersion = readFileSync(new URL('../app_version.py', import.meta.url), 'utf8')
  .match(/__version__\s*=\s*"([^"]+)"/)?.[1] ?? '0.0.0'

// https://vite.dev/config/
export default defineConfig({
  define: {
    __APP_VERSION__: JSON.stringify(appVersion)
  },
  plugins: [
    react(),
    tailwindcss()
  ],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://127.0.0.1:49221',
      '/media': 'http://127.0.0.1:49221'
    }
  }
})
