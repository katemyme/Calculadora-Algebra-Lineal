// Opción 9 del Programa 3: resolver la ecuación matricial A·x = b.
// Reutiliza la rejilla [A | b] del Programa 2.

import { useState } from "react";
import { ErrorDeCalculo, programa3 } from "../../lib/api.js";
import Boton from "../ui/Boton.jsx";
import ConfiguracionSistema from "../ConfiguracionSistema.jsx";
import MatrizAumentada from "../MatrizAumentada.jsx";
import ResultadoSistema from "./ResultadoSistema.jsx";
import {
  AvisoError,
  Cargando,
  DIMENSION_MAXIMA,
  DIMENSION_MINIMA,
  cambiarCelda,
  redimensionarRejilla,
  redimensionarVector,
  useOperacion,
} from "./comunes.jsx";

const CASOS = [
  {
    nombre: "Única",
    A: [["2", "1", "-1"], ["-3", "-1", "2"], ["-2", "1", "2"]],
    b: ["8", "-11", "-3"],
  },
  {
    nombre: "Infinitas",
    A: [["1", "2", "1"], ["2", "4", "3"]],
    b: ["4", "9"],
  },
  {
    nombre: "Inconsistente",
    A: [["1", "1"], ["2", "2"]],
    b: ["2", "5"],
  },
];

export default function SeccionEcuacion() {
  const [A, setA] = useState(CASOS[0].A.map((f) => [...f]));
  const [b, setB] = useState([...CASOS[0].b]);
  const { resultado, error, cargando, ejecutar, limpiar } = useOperacion();

  const m = A.length;
  const n = A[0].length;

  function redimensionar(filas, columnas) {
    setA(redimensionarRejilla(A, filas, columnas));
    setB(redimensionarVector(b, filas));
    limpiar();
  }

  // La rejilla del Programa 2 numera b como columna n + 1.
  let celdaError = null;
  if (error instanceof ErrorDeCalculo && error.fila) {
    if (error.campo === "A") celdaError = { fila: error.fila, columna: error.columna };
    if (error.campo === "b") celdaError = { fila: error.fila, columna: n + 1 };
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <ConfiguracionSistema
          m={m}
          n={n}
          minimo={DIMENSION_MINIMA}
          maximo={DIMENSION_MAXIMA}
          onCambiarM={(nuevo) => redimensionar(nuevo, n)}
          onCambiarN={(nuevo) => redimensionar(m, nuevo)}
          columnasAumentada={n + 1}
        />
        <div className="flex flex-wrap gap-2">
          {CASOS.map((caso) => (
            <Boton
              key={caso.nombre}
              variante="secundario"
              className="text-xs"
              onClick={() => {
                setA(caso.A.map((f) => [...f]));
                setB([...caso.b]);
                limpiar();
              }}
            >
              {caso.nombre}
            </Boton>
          ))}
        </div>
      </div>

      <div className="math-formula-strip" aria-hidden="true">
        <span>A·x = b</span>
        <span>[A | b] → RREF</span>
        <span>verificación: A·x con el producto matricial</span>
      </div>

      <MatrizAumentada
        coeficientes={A}
        terminos={b}
        onCambiarCoeficiente={(i, j, valor) => {
          setA(cambiarCelda(A, i, j, valor));
          limpiar();
        }}
        onCambiarTermino={(i, valor) => {
          setB(b.map((v, k) => (k === i ? valor : v)));
          limpiar();
        }}
        celdaError={celdaError}
      />

      <Boton
        onClick={() => ejecutar(() => programa3.ecuacion({ A, b }))}
        disabled={cargando}
      >
        {cargando ? "Resolviendo…" : "Resolver A·x = b"}
      </Boton>

      {cargando && <Cargando texto="Resolviendo [A | b]…" />}
      <AvisoError error={error} />
      {resultado && <ResultadoSistema resultado={resultado} modo="ecuacion" />}
    </div>
  );
}
