// Contenedor del botón "Transformaciones Lineales": una pestaña para la
// fórmula general y otra para los vectores dados (imágenes de una base). Cada
// sección conserva su estado al cambiar de una a otra (se ocultan en lugar de
// desmontarse).

import { useState } from "react";
import Panel from "../ui/Panel.jsx";
import SeccionFormula from "./SeccionFormula.jsx";
import SeccionVectores from "./SeccionVectores.jsx";

const SECCIONES = [
  {
    id: "formula",
    simbolo: "T(x, y) = (…)",
    titulo: "Fórmula general",
    descripcion:
      "Escriba T por su fórmula. Se prueba si es lineal (T(0), aditividad y homogeneidad) " +
      "y, si lo es, se hallan su matriz, núcleo, nulidad, imagen y rango paso a paso.",
    Componente: SeccionFormula,
  },
  {
    id: "vectores",
    simbolo: "T(1, 0) = (…)",
    titulo: "Vectores dados",
    descripcion:
      "Dé las imágenes de una base de ℝⁿ. Se calcula T(v) por linealidad, la matriz de T " +
      "y su núcleo, nulidad, imagen y rango paso a paso.",
    Componente: SeccionVectores,
  },
];

export default function ProgramaTransformaciones() {
  const [activa, setActiva] = useState("formula");
  const seccion = SECCIONES.find((s) => s.id === activa);

  return (
    <div className="space-y-7">
      <nav className="p3-selector" aria-label="Opciones de Transformaciones Lineales">
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
