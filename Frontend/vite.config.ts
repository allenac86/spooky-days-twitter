import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { defineConfig } from "vite";
import tsconfigPaths from "vite-tsconfig-paths";

export default defineConfig({
  plugins: [tailwindcss(), react(), tsconfigPaths()],
  server: {
    proxy: {
      '/api': {
        target: process.env.SPOOKY_URL,
        changeOrigin: true,
        secure: true,
      },
    },
  },
  build: {
    outDir: 'build',
    ssr: false,
  },
});
