/**
 * Vite configuration for Sleep Research Platform
 * Configured with React and Tailwind CSS v4 plugin
 */
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
})
