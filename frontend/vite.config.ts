import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'


// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/auth': 'http://localhost:8002',
      '/classes': 'http://localhost:8001',
      '/upload': 'http://localhost:8001',
      '/documents': 'http://localhost:8001',
      '/query': 'http://localhost:8000',
      // Add more endpoints as needed
    }
  }
})
