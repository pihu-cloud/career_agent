import { defineConfig } from 'vite';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// https://vitejs.dev/config/
export default defineConfig({
  esbuild: {
    jsx: 'automatic',
  },
  resolve: {
    alias: {
      '@heroicons/react/24/outline': path.resolve(__dirname, 'src/shims/heroicons.jsx'),
      '@headlessui/react': path.resolve(__dirname, 'src/shims/headlessui.jsx'),
      'react-hook-form': path.resolve(__dirname, 'src/shims/react-hook-form.js'),
      '@hookform/resolvers/zod': path.resolve(__dirname, 'src/shims/hookform-resolvers.js'),
      'react-hot-toast': path.resolve(__dirname, 'src/shims/react-hot-toast.jsx'),
      'recharts': path.resolve(__dirname, 'src/shims/recharts.jsx'),
      'react-dropzone': path.resolve(__dirname, 'src/shims/react-dropzone.jsx'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
});
