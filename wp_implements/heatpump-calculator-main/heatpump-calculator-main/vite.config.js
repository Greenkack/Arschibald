// vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  // IMPORTANT: replace REPO_NAME with your repository name
  base: '/heatpump-calculator/',
})
