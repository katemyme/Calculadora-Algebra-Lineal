// Contenedor del botón "Álgebra de Matrices" (Programa 5, Módulo III): las
// operaciones básicas, el determinante (una pestaña por método: cofactores,
// Sarrus y triangular), la Regla de Cramer, la inversa, el verificador de
// propiedades y los teoremas clave. Cada sección conserva su estado al cambiar
// de una a otra (se ocultan en lugar de desmontarse).

import { useState } from "react";
import Panel from "../ui/Panel.jsx";
import SeccionCramer from "./SeccionCramer.jsx";
import SeccionDeterminante, { ProveedorDeterminante } from "./SeccionDeterminante.jsx";
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
  // Opción 6: det(A) por tres métodos. Comparten la matriz (ProveedorDeterminante).
  {
    id: "cofactores",
    simbolo: "det · C₁ⱼ",
    titulo: "Cofactores",
    descripcion:
      "Determinante por expansión por cofactores sobre la fila 1, paso a paso: cada " +
      "menor M₁ⱼ, su cofactor C₁ⱼ y la suma de los productos a₁ⱼ·C₁ⱼ (opción 6).",
    Componente: SeccionDeterminante,
    props: { metodo: "cofactores" },
  },
  {
    id: "sarrus",
    simbolo: "det · ↘↗",
    titulo: "Regla de Sarrus",
    descripcion:
      "Determinante de una matriz 3×3, paso a paso: los tres productos de las diagonales " +
      "descendentes menos los tres de las ascendentes (opción 6).",
    Componente: SeccionDeterminante,
    props: { metodo: "sarrus" },
  },
  {
    id: "triangular",
    simbolo: "det · ◥",
    titulo: "Triangular",
    descripcion:
      "Determinante por reducción a forma triangular, paso a paso: cada operación de " +
      "fila, el producto de la diagonal y el signo por los intercambios (opción 6).",
    Componente: SeccionDeterminante,
    props: { metodo: "triangular" },
  },
  {
    id: "cramer",
    simbolo: "Aᵢ(b)",
    titulo: "Regla de Cramer",
    descripcion:
      "Resuelve el sistema Ax = b con xᵢ = det Aᵢ(b) / det A, i = 1, 2, …, n, " +
      "mostrando cada matriz Aᵢ(b), su determinante y la comprobación A·x = b.",
    Componente: SeccionCramer,
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
      "Con A y B invertibles del mismo orden, calcula ambos miembros de siete " +
      "propiedades de la inversa y del determinante (opción 9).",
    Componente: SeccionVerificador,
  },
  {
    id: "teoremas",
    simbolo: "⇔",
    titulo: "Teoremas clave",
    descripcion:
      "Transpuesta, teorema de la inversa, Teorema de la Matriz Invertible, " +
      "relación entre determinante e inversa y Factorización LU (opción 0).",
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
        <ProveedorDeterminante>
          {SECCIONES.map(({ id, Componente, props }) => (
            <div key={id} hidden={id !== activa}>
              <Componente {...props} />
            </div>
          ))}
        </ProveedorDeterminante>
      </Panel>
    </div>
  );
}
