import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/generate-plan': 'http://localhost:5050',
      '/log-session':   'http://localhost:5050',
      '/history':       'http://localhost:5050',
      '/exercises-logged': 'http://localhost:5050',
      '/suggest':       'http://localhost:5050',
    }
  }
})
