import { defineConfig } from "vite"
import react from "@vitejs/plugin-react-swc"

export default defineConfig({
  plugins: [react()],
    build: {
      outDir: "dist",
    },
  server: {
    allowedHosts: [
      "6907-2804-6888-872c-1-77df-53c0-f590-c24f.ngrok-free.app",
    ],
  },
})