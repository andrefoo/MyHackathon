// vite.config.js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    exclude: ['@tensorflow-models/coco-ssd']
  },
  build: {
    sourcemap: false,
    rollupOptions: {
      output: {
        sourcemap: false
      }
    }
  }
});
