// Opción 4 del Programa 3: ¿b = c₁·v₁ + … + cₖ·vₖ?
// Los vectores se editan como COLUMNAS de la matriz [v₁ … vₖ | b].

import { useState } from "react";
import { ErrorDeCalculo, programa3 } from "../../lib/api.js";
import { subindice } from "../../lib/formato.js";
import Boton from "../ui/Boton.jsx";
import SelectorDimension from "../ui/SelectorDimension.jsx";
import ResultadoSistema from "./ResultadoSistema.jsx";
import {
  AvisoError,
  Cargando,
  DIMENSION_MAXIMA,
  DIMENSION_MINIMA,
  EditorMatriz,
  cambiarCelda,
  redimensionarRejilla,
  useOperacion,
} from "./comunes.jsx";

// Cada caso se da como lista de vectores (columnas) y b.
const CASOS = [
  {
    nombre: "SÍ (única)",
    vectores: [["1", "-2", "-5"], ["2", "5", "6"]],
    b: ["7", "4", "-3"],
  },
  {
    nombre: "NO",
    vectores: [["1", "0", "0"], ["0", "1", "0"]],
    b: ["0", "0", "1"],
  },
  {
    nombre: "Infinitas",
    vectores: [["1", "1"], ["2", "2"], ["0", "1"]],
    b: ["3", "4"],
  },
];

/** Rejilla n×(k+1): columna j = vⱼ, última columna = b. */
function rejillaDesdeCaso(caso) {
  return caso.b.map((bi, i) => [...caso.vectores.map((v) => v[i]), bi]);
}

export default function SeccionCombinacion() {
  // Rejilla n filas × (k + 1) columnas; empieza con n = 3, k = 2.
  const [rejilla, setRejilla] = useState(rejillaDesdeCaso(CASOS[0]));
  const { resultado, error, cargando, ejecutar, limpiar } = useOperacion();

  const n = rejilla.length;
  const k = rejilla[0].length - 1;

  const encabezados = [
    ...Array.from({ length: k }, (_, j) => `v${subindice(j + 1)}`),
    "b",
  ];

  function redimensionar(nuevoN, nuevoK) {
    // Se conserva la columna b como última columna.
    const b = rejilla.map((fila) => fila[k]);
    const vectores = redimensionarRejilla(rejilla.map((fila) => fila.slice(0, k)), nuevoN, nuevoK);
    setRejilla(vectores.map((fila, i) => [...fila, b[i] ?? ""]));
    limpiar();
  }

  function calcular() {
    const vectores = Array.from({ length: k }, (_, j) => rejilla.map((fila) => fila[j]));
    const b = rejilla.map((fila) => fila[k]);
    ejecutar(() => programa3.combinacion({ vectores, b }));
  }

  // Errores: "vectores" trae columna j; "b" solo fila → última columna.
  let celdaError = null;
  if (error instanceof ErrorDeCalculo && error.fila) {
    if (error.campo === "vectores") celdaError = { fila: error.fila, columna: error.columna };
    if (error.campo === "b") celdaError = { fila: error.fila, columna: k + 1 };
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap gap-x-8 gap-y-3">
          <SelectorDimension
            id="comb-n"
            etiqueta="Dimensión n"
            valor={n}
            minimo={DIMENSION_MINIMA}
            maximo={DIMENSION_MAXIMA}
            onCambiar={(nuevo) => redimensionar(nuevo, k)}
          />
          <SelectorDimension
            id="comb-k"
            etiqueta="Vectores k"
            valor={k}
            minimo={DIMENSION_MINIMA}
            maximo={DIMENSION_MAXIMA}
            onCambiar={(nuevo) => redimensionar(n, nuevo)}
          />
        </div>
        <div className="flex flex-wrap gap-2">
          {CASOS.map((caso) => (
            <Boton
              key={caso.nombre}
              variante="secundario"
              className="text-xs"
              onClick={() => {
                setRejilla(rejillaDesdeCaso(caso));
                limpiar();
              }}
            >
              {caso.nombre}
            </Boton>
          ))}
        </div>
      </div>

      <div className="math-formula-strip" aria-hidden="true">
        <span>c₁·v₁ + c₂·v₂ + … + cₖ·vₖ = b</span>
        <span>vectores como columnas</span>
        <span>[v₁ … vₖ | b] → Gauss-Jordan</span>
      </div>

      <div className="p3-lienzo">
        <EditorMatriz
          etiqueta="Combinación"
          valores={rejilla}
          encabezados={encabezados}
          separarUltima
          celdaError={celdaError}
          onCambiar={(i, j, texto) => {
            setRejilla(cambiarCelda(rejilla, i, j, texto));
            limpiar();
          }}
        />
        <p className="max-w-xs text-xs text-grafito">
          Cada <strong>columna</strong> es un vector de ℝ<sup>{n}</sup>. La última
          columna es b. Celda vacía = 0.
        </p>
      </div>

      <Boton onClick={calcular} disabled={cargando}>
        {cargando ? "Resolviendo…" : "¿Es combinación lineal?"}
      </Boton>

      {cargando && <Cargando texto="Resolviendo [v₁ … vₖ | b]…" />}
      <AvisoError error={error} />
      {resultado && <ResultadoSistema resultado={resultado} modo="combinacion" />}
    </div>
  );
}
