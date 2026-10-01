// Vectores → Independencia Lineal (Programa 4).
// El usuario elige k (cantidad de vectores) y n (dimensión) y escribe cada
// vector como COLUMNA de A. El backend arma [A | 0], lo reduce por filas y
// devuelve la matriz reducida, los pivotes y el veredicto L.I. / L.D.

import { useState } from "react";
import { ErrorDeCalculo, programa4 } from "../../lib/api.js";
import { subindice } from "../../lib/formato.js";
import Boton from "../ui/Boton.jsx";
import SelectorDimension from "../ui/SelectorDimension.jsx";
import ResultadoIndependenciaLineal from "./ResultadoIndependenciaLineal.jsx";
import {
  AvisoError,
  Cargando,
  DIMENSION_MAXIMA,
  DIMENSION_MINIMA,
  EditorMatriz,
  cambiarCelda,
  redimensionarRejilla,
  useOperacion,
} from "../programa3/comunes.jsx";

// Cada caso es la lista de vectores (se colocan como columnas).
const CASOS = [
  {
    nombre: "L.I. en ℝ³",
    vectores: [
      ["1", "0", "2"],
      ["0", "1", "1"],
      ["1", "1", "0"],
    ],
  },
  {
    nombre: "L.D. (v₂ = 2v₁)",
    vectores: [
      ["1", "2", "3"],
      ["2", "4", "6"],
      ["1", "0", "1"],
    ],
  },
  {
    nombre: "k > n",
    vectores: [
      ["1", "0"],
      ["0", "1"],
      ["2", "3"],
    ],
  },
];

/** Rejilla n × k: cada columna es un vector del caso. */
function rejillaDesdeCaso(caso) {
  const n = caso.vectores[0].length;
  return Array.from({ length: n }, (_, i) => caso.vectores.map((v) => v[i]));
}

export default function SeccionIndependenciaLineal() {
  const [rejilla, setRejilla] = useState(() =>
    redimensionarRejilla([], 3, 3)
  );
  const { resultado, error, cargando, ejecutar, limpiar } = useOperacion();

  const n = rejilla.length; // dimensión de cada vector
  const k = rejilla[0].length; // cantidad de vectores
  const encabezados = Array.from({ length: k }, (_, j) => `v${subindice(j + 1)}`);

  function redimensionar(nuevoN, nuevoK) {
    setRejilla(redimensionarRejilla(rejilla, nuevoN, nuevoK));
    limpiar();
  }

  function vectoresActuales() {
    return Array.from({ length: k }, (_, j) => rejilla.map((fila) => fila[j]));
  }

  function calcular() {
    ejecutar(() => programa4.independencia({ vectores: vectoresActuales() }));
  }

  const celdaError =
    error instanceof ErrorDeCalculo && error.campo === "vectores" && error.fila
      ? { fila: error.fila, columna: error.columna }
      : null;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap gap-x-8 gap-y-3">
          <SelectorDimension
            id="p4-k"
            etiqueta="Cantidad de vectores k"
            valor={k}
            minimo={DIMENSION_MINIMA}
            maximo={DIMENSION_MAXIMA}
            onCambiar={(nuevo) => redimensionar(n, nuevo)}
          />
          <SelectorDimension
            id="p4-n"
            etiqueta="Dimensión n"
            valor={n}
            minimo={DIMENSION_MINIMA}
            maximo={DIMENSION_MAXIMA}
            onCambiar={(nuevo) => redimensionar(nuevo, k)}
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
          <Boton
            variante="fantasma"
            className="text-xs"
            onClick={() => {
              setRejilla(redimensionarRejilla([], n, k));
              limpiar();
            }}
          >
            Limpiar
          </Boton>
        </div>
      </div>

      <div className="math-formula-strip" aria-hidden="true">
        <span>c₁v₁ + c₂v₂ + … + cₖvₖ = 0</span>
        <span>pivotes = k ⇒ L.I.</span>
        <span>pivotes &lt; k ⇒ L.D.</span>
      </div>

      <div className="p3-lienzo">
        <EditorMatriz
          etiqueta="Vectores"
          valores={rejilla}
          encabezados={encabezados}
          celdaError={celdaError}
          onCambiar={(i, j, texto) => {
            setRejilla(cambiarCelda(rejilla, i, j, texto));
            limpiar();
          }}
        />
        <p className="max-w-xs text-xs text-grafito">
          Cada <strong>columna</strong> es un vector de ℝ<sup>{n}</sup>. Se forma la
          matriz A = [v₁ … v<sub>k</sub>] y el sistema homogéneo{" "}
          <strong>Ax = 0</strong>. Acepta enteros, decimales y fracciones (1/2).
          Celda vacía = 0.
        </p>
      </div>

      <Boton onClick={calcular} disabled={cargando}>
        {cargando ? "Reduciendo…" : "Evaluar independencia lineal"}
      </Boton>

      {cargando && <Cargando texto="Reduciendo [A | 0] por filas…" />}
      <AvisoError error={error} />
      {resultado && <ResultadoIndependenciaLineal resultado={resultado} />}
    </div>
  );
}
