// Vista del Programa 9 (botón "Newton-Raphson"): métodos abiertos en cuatro pestañas.
// Cada sección conserva su estado al cambiar de pestaña (se ocultan en lugar de desmontarse).
// Aquí solo se capturan datos y se muestran resultados: no se calcula nada en JavaScript.

import { useEffect, useState } from "react";
import { programa9 } from "../../lib/api.js";
import { POR_DEFECTO } from "./comunes.jsx";
import SeccionDerivadas from "./SeccionDerivadas.jsx";
import SeccionNewton from "./SeccionNewton.jsx";
import SeccionPolinomios from "./SeccionPolinomios.jsx";
import SeccionSecante from "./SeccionSecante.jsx";

const SECCIONES = [
  { id: "newton", simbolo: "xᵢ − f(xᵢ)/f′(xᵢ)", titulo: "1 · Newton-Raphson" },
  { id: "secante", simbolo: "sin f′(x)", titulo: "2 · Secante" },
  { id: "derivadas", simbolo: "f′ ≈ Δf / h", titulo: "3 · Derivadas numéricas" },
  { id: "polinomios", simbolo: "p(x) ÷ (x − r)", titulo: "4 · Polinomios" },
];

const SIN_EJEMPLOS = {
  casos: [],
  adicionales: [],
  clase: [],
  secante: [],
  derivadas: [],
  polinomios: [],
  por_defecto: POR_DEFECTO,
};

export default function ProgramaNewtonRaphson() {
  const [activa, setActiva] = useState("newton");
  const [ejemplos, setEjemplos] = useState(SIN_EJEMPLOS);

  // Los ejemplos viven en el backend (una sola fuente de verdad).
  useEffect(() => {
    programa9
      .ejemplos()
      .then((datos) => setEjemplos({ ...SIN_EJEMPLOS, ...datos }))
      .catch(() => {});
  }, []);

  return (
    <div className="space-y-7">
      <nav className="p3-selector" aria-label="Opciones de métodos abiertos">
        {SECCIONES.map((s) => (
          <button
            key={s.id}
            type="button"
            aria-pressed={s.id === activa}
            onClick={() => setActiva(s.id)}
            className="p3-selector-boton"
          >
            <span className="p3-selector-simbolo">{s.simbolo}</span>
            <span className="p3-selector-texto">{s.titulo}</span>
          </button>
        ))}
      </nav>

      <div hidden={activa !== "newton"}>
        <SeccionNewton ejemplos={ejemplos} />
      </div>
      <div hidden={activa !== "secante"}>
        <SeccionSecante ejemplos={ejemplos} />
      </div>
      <div hidden={activa !== "derivadas"}>
        <SeccionDerivadas ejemplos={ejemplos} />
      </div>
      <div hidden={activa !== "polinomios"}>
        <SeccionPolinomios ejemplos={ejemplos} />
      </div>
    </div>
  );
}
