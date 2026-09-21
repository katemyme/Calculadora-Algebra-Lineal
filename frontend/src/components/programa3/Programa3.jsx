// Contenedor del Programa 3: operaciones en ℝⁿ, combinación lineal,
// independencia lineal y ecuaciones matriciales. Cada sección conserva su estado al cambiar de una a
// otra (se ocultan en lugar de desmontarse).

import { useState } from "react";
import Panel from "../ui/Panel.jsx";
import SeccionVectores from "./SeccionVectores.jsx";
import SeccionCombinacion from "./SeccionCombinacion.jsx";
import SeccionIndependencia from "./SeccionIndependencia.jsx";
import SeccionMatrices from "./SeccionMatrices.jsx";
import SeccionProducto from "./SeccionProducto.jsx";
import SeccionEcuacion from "./SeccionEcuacion.jsx";

const SECCIONES = [
  {
    id: "vectores",
    simbolo: "u ± v",
    titulo: "Vectores ℝⁿ",
    descripcion: "Suma, resta y producto por escalar de vectores (opciones 1–3).",
    Componente: SeccionVectores,
  },
  {
    id: "combinacion",
    simbolo: "Σ cᵢvᵢ",
    titulo: "Combinación lineal",
    descripcion: "¿Se puede escribir b como c₁·v₁ + … + cₖ·vₖ? (opción 4).",
    Componente: SeccionCombinacion,
  },
  {
    id: "independencia",
    simbolo: "Σ cᵢvᵢ = 0",
    titulo: "Independencia lineal",
    descripcion:
      "¿Es c₁·v₁ + … + cₖ·vₖ = 0 solo con todos los cᵢ = 0? (opción 10).",
    Componente: SeccionIndependencia,
  },
  {
    id: "matrices",
    simbolo: "A ± B",
    titulo: "Matrices",
    descripcion: "Suma, resta y producto por escalar de matrices (opciones 5–7).",
    Componente: SeccionMatrices,
  },
  {
    id: "producto",
    simbolo: "A · B",
    titulo: "Producto matricial",
    descripcion: "cᵢⱼ = Σₖ aᵢₖ·bₖⱼ con tres bucles anidados (opción 8).",
    Componente: SeccionProducto,
  },
  {
    id: "ecuacion",
    simbolo: "Ax = b",
    titulo: "Ecuación matricial",
    descripcion: "Resolver y clasificar A·x = b y verificar con A·x (opción 9).",
    Componente: SeccionEcuacion,
  },
];

export default function Programa3() {
  const [activa, setActiva] = useState("vectores");
  const seccion = SECCIONES.find((s) => s.id === activa);

  return (
    <div className="space-y-7">
      <nav className="p3-selector" aria-label="Secciones del Programa 3">
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

      <Panel className="math-panel overflow-hidden" titulo={seccion.titulo} descripcion={seccion.descripcion}>
        {SECCIONES.map(({ id, Componente }) => (
          <div key={id} hidden={id !== activa}>
            <Componente />
          </div>
        ))}
      </Panel>
    </div>
  );
}
