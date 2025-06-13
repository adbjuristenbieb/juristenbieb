import { defineConfig } from 'astro/config';

export default defineConfig({
  output: 'server',
  vite: {
    server: {
      allowedHosts: ['4453-86-87-55-212.ngrok-free.app']
    }
  }
});