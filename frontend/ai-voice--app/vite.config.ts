import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'


// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  server: {
    host: '0.0.0.0',
    port: 80,
    proxy: {
      '/api': {
        target: 'https://ai-voice-qa-poker-rules-backend-production.up.railway.app',
        changeOrigin: true,
        secure: true,
      },
    },
  },
  preview: {
    port: 80,
    allowedHosts: [
      'ai-voice-qa-poker-rules.up.railway.app',
      'https://ai-voice-qa-poker-rules-backend-production.up.railway.app'
    ],
  },
})
