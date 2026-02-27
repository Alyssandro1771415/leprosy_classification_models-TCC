import { defineConfig } from "vite"
import react from "@vitejs/plugin-react-swc"

export default defineConfig({
  plugins: [react()],
    build: {
      outDir: "dist",
    },
  server: {
    allowedHosts: [
      "6c05-2804-6888-872c-1-cdbd-c780-1f66-2d8a.ngrok-free.app",
    ],
  },
})