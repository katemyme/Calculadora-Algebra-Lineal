import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// El servidor de desarrollo corre en el puerto 5173, que es el único origen
// que el backend (FastAPI) autoriza en su configuración de CORS.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: true,
  },
});
