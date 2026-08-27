import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";
import "./index.css";

// Punto de arranque de la interfaz. El frontend solo recoge datos, los envía
// al backend y pinta la respuesta: aquí no ocurre ningún cálculo matemático.
ReactDOM.createRoot(document.getElementById("raiz")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
