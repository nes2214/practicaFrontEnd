import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    assetsDir: 'static',
  },
  server: {
    proxy: {
      "/api/time ":'http://localhost:8000',
    },
  },
})
