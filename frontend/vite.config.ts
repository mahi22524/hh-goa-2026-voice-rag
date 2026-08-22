import { defineConfig } from "vite";
import tsconfigPaths from "vite-tsconfig-paths";
import { tanstackStart } from "@tanstack/react-start/plugin/vite";
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  base: "/hh-goa-2026-voice-rag/",
  plugins: [
    tsconfigPaths(),
    tailwindcss(),
    tanstackStart({
      spa: {
        enabled: true,
      },
    }),
    react(),
  ],
});
