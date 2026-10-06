// Contenedor del botón "Álgebra de Matrices" (Programa 5, Módulo III): las
// operaciones básicas, el determinante, la inversa, el verificador de
// propiedades y los teoremas clave. Cada sección conserva su estado al cambiar
// de una a otra (se ocultan en lugar de desmontarse).

import { useState } from "react";
import Panel from "../ui/Panel.jsx";
import SeccionDeterminante from "./SeccionDeterminante.jsx";
import SeccionInversa from "./SeccionInversa.jsx";
import SeccionOperaciones from "./SeccionOperaciones.jsx";
import SeccionTeoremas from "./SeccionTeoremas.jsx";
import SeccionVerificador from "./SeccionVerificador.jsx";

const SECCIONES = [
  {
    id: "operaciones",
    simbolo: "A ± B",
    titulo: "Operaciones",
    descripcion:
      "Suma, resta, multiplicación por escalar, producto matricial y transposición, " +
      "con la validación de dimensiones (opciones 1–5).",
    Componente: SeccionOperaciones,
  },
  {
    id: "determinante",
    simbolo: "det A",
    titulo: "Determinante",
    descripcion:
      "Expansión por cofactores, regla de Sarrus y reducción a forma triangular; " +
      "se comprueba que los métodos coinciden (opción 6).",
    Componente: SeccionDeterminante,
  },
  {
    id: "inversa",
    simbolo: "A⁻¹",
    titulo: "Inversa",
    descripcion:
      "Por Gauss-Jordan sobre [A | I] o por la matriz adjunta, con la comprobación " +
      "A·A⁻¹ = I y el diagnóstico de invertibilidad (opciones 7 y 8).",
    Componente: SeccionInversa,
  },
  {
    id: "verificador",
    simbolo: "✓ ✗",
    titulo: "Verificador",
    descripcion:
      "Con A y B invertibles del mismo orden, calcula ambos miembros de seis " +
      "propiedades de la inversa y del determinante (opción 9).",
    Componente: SeccionVerificador,
  },
  {
    id: "teoremas",
    simbolo: "⇔",
    titulo: "Teoremas clave",
    descripcion:
      "Transpuesta, teorema de la inversa, Teorema de la Matriz Invertible y " +
      "relación entre determinante e inversa (opción 0).",
    Componente: SeccionTeoremas,
  },
];

export default function Programa5() {
  const [activa, setActiva] = useState("operaciones");
  const seccion = SECCIONES.find((s) => s.id === activa);

  return (
    <div className="space-y-7">
      <nav className="p3-selector" aria-label="Opciones de Álgebra de Matrices">
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
