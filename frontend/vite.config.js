import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// VITE_API_BASE_URL controls where the frontend talks to the FastAPI backend.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true,
  },
});
