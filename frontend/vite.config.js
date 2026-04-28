import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'https://8ur8lkoioe.execute-api.us-east-1.amazonaws.com/deploy',
        changeOrigin: true,
        secure: false,
      }
    }
  }
})
