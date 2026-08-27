/** @type {import('tailwindcss').Config} */

// Los mismos valores viven como variables CSS en src/index.css para poder
// usarlos en SVG y estilos en línea (por ejemplo, la escalera de pivotes).
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        // --- Sustrato y tinta (papel técnico frío) ---
        papel: "#EEF1F6", // fondo de la aplicación
        superficie: "#FFFFFF", // tarjetas y paneles
        tinta: "#0F1B2D", // texto principal
        grafito: "#5A6884", // texto secundario y encabezados
        // --- Acento reservado para los pivotes ---
        pivote: "#6D3BEB", // pivotes, foco de teclado, elementos activos
        // --- Colores semánticos de la clasificación ---
        determinado: "#0E9F6E",
        indeterminado: "#C77700",
        inconsistente: "#D63C4A",
      },
      fontFamily: {
        display: ['"Space Grotesk"', "system-ui", "sans-serif"],
        cuerpo: ['"IBM Plex Sans"', "system-ui", "sans-serif"],
        mono: ['"IBM Plex Mono"', "ui-monospace", "SFMono-Regular", "monospace"],
      },
    },
  },
  plugins: [],
};
