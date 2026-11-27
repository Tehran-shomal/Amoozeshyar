import { fileURLToPath } from "node:url";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const projectRoot = fileURLToPath(new URL(".", import.meta.url));

export default defineConfig({
  root: projectRoot,
  base: "/static/core/react-build/",
  plugins: [react()],
  build: {
    outDir: "../static/core/react-build",
    emptyOutDir: true,
    assetsDir: "",
    cssCodeSplit: false,
    rolldownOptions: {
      output: {
        entryFileNames: "app.js",
        chunkFileNames: "chunks/[name]-[hash].js",
        assetFileNames: "[name][extname]",
      },
    },
  },
});
