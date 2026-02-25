import { defineConfig } from "vite"
import react from "@vitejs/plugin-react-swc"

export default defineConfig({
  plugins: [react()],
  server: {
    allowedHosts: [
      "f3ed-2804-6888-872c-1-1cf2-5088-5e71-7bb1.ngrok-free.app",
    ],
  },
})