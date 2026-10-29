// Contenedor del botón "Vectores" (Programa 4): Independencia Lineal y
// Demostración de subespacio. Cada sección conserva su estado al cambiar de
// una a otra (se ocultan en lugar de desmontarse).

import { useState } from "react";
import Panel from "../ui/Panel.jsx";
import SeccionIndependenciaLineal from "./SeccionIndependenciaLineal.jsx";
import SeccionSubespacio from "./SeccionSubespacio.jsx";

const SECCIONES = [
  {
    id: "independencia",
    simbolo: "Ax = 0",
    titulo: "Independencia Lineal",
    descripcion:
      "Indique la cantidad de vectores k y su dimensión n. Se construye el sistema " +
      "homogéneo Ax = 0, se reduce por filas y se cuentan pivotes y variables libres.",
    Componente: SeccionIndependenciaLineal,
  },
  {
    id: "subespacio",
    simbolo: "H ≤ V",
    titulo: "Demostración de subespacio",
    descripcion:
      "Escriba el conjunto y su hipótesis. Se demuestran las cuatro condiciones " +
      "(i) H ⊂ V, (ii) 0 ∈ H, (iii) cerradura bajo la suma y (iv) bajo el escalar, " +
      "y se obtienen los generadores, la base y la combinación lineal.",
    Componente: SeccionSubespacio,
  },
];

export default function Programa4() {
  const [activa, setActiva] = useState("independencia");
  const seccion = SECCIONES.find((s) => s.id === activa);

  return (
    <div className="space-y-7">
      <nav className="p3-selector" aria-label="Opciones de Vectores">
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
