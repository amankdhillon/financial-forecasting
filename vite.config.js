import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: { open: true, port: 5173 },
  // Root-level entry to avoid clashing with the Python src/ directory
  build: { rollupOptions: { input: "index.html" } },
  base: "/financial-forecasting/",

});
