// Opción 10 del Programa 3: ¿son v₁, …, vₖ linealmente independientes?
// Los vectores se editan como COLUMNAS de la matriz [v₁ … vₖ], que el backend
// completa con la columna de ceros para formar el sistema homogéneo.

import { useState } from "react";
import { ErrorDeCalculo, programa3 } from "../../lib/api.js";
import { subindice } from "../../lib/formato.js";
import Boton from "../ui/Boton.jsx";
import SelectorDimension from "../ui/SelectorDimension.jsx";
import ResultadoIndependencia from "./ResultadoIndependencia.jsx";
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

// Cada caso es la lista de vectores puestos como columnas.
const CASOS = [
  {
    nombre: "Independientes",
    vectores: [["1", "0", "0"], ["0", "1", "0"], ["0", "0", "1"]],
  },
  {
    nombre: "Dependientes",
    vectores: [["1", "2", "3"], ["2", "4", "6"], ["1", "0", "1"]],
  },
  {
    nombre: "k > n",
    vectores: [["1", "0"], ["0", "1"], ["2", "3"]],
  },
  {
    nombre: "Con vector 0",
    vectores: [["1", "2"], ["0", "0"]],
  },
];

/** Rejilla n×k: la columna j es el vector vⱼ. */
function rejillaDesdeCaso(caso) {
  const n = caso.vectores[0].length;
  return Array.from({ length: n }, (_, i) => caso.vectores.map((v) => v[i]));
}

export default function SeccionIndependencia() {
  // Rejilla n filas × k columnas; empieza con la base canónica de ℝ³.
  const [rejilla, setRejilla] = useState(rejillaDesdeCaso(CASOS[0]));
  const { resultado, error, cargando, ejecutar, limpiar } = useOperacion();

  const n = rejilla.length;
  const k = rejilla[0].length;

  const encabezados = Array.from({ length: k }, (_, j) => `v${subindice(j + 1)}`);

  function redimensionar(nuevoN, nuevoK) {
    setRejilla(redimensionarRejilla(rejilla, nuevoN, nuevoK));
    limpiar();
  }

  function vectoresActuales() {
    return Array.from({ length: k }, (_, j) => rejilla.map((fila) => fila[j]));
  }

  function calcular() {
    ejecutar(() => programa3.independencia({ vectores: vectoresActuales() }));
  }

  async function evaluarParametros(valoresParametros) {
    const datos = await programa3.independencia({
      vectores: vectoresActuales(),
      valores_parametros: valoresParametros,
    });
    return datos.evaluacion_parametros;
  }

  // El backend reporta los errores de "vectores" con fila y columna.
  let celdaError = null;
  if (error instanceof ErrorDeCalculo && error.campo === "vectores" && error.fila) {
    celdaError = { fila: error.fila, columna: error.columna };
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap gap-x-8 gap-y-3">
          <SelectorDimension
            id="indep-n"
            etiqueta="Dimensión n"
            valor={n}
            minimo={DIMENSION_MINIMA}
            maximo={DIMENSION_MAXIMA}
            onCambiar={(nuevo) => redimensionar(nuevo, k)}
          />
          <SelectorDimension
            id="indep-k"
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
        <span>x₁·v₁ + x₂·v₂ + … + xₖ·vₖ = 0</span>
        <span>rango = k ⇒ independientes</span>
        <span>rango &lt; k ⇒ dependientes</span>
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
          Cada <strong>columna</strong> es un vector de ℝ<sup>{n}</sup>. Se resuelve el
          sistema <strong>homogéneo</strong> [v₁ … v<sub>k</sub> | 0]. Celda vacía = 0.
        </p>
      </div>

      <Boton onClick={calcular} disabled={cargando}>
        {cargando ? "Analizando…" : "¿Son linealmente independientes?"}
      </Boton>

      {cargando && <Cargando texto="Reduciendo [v₁ … vₖ | 0]…" />}
      <AvisoError error={error} />
      {resultado && (
        <ResultadoIndependencia resultado={resultado} onEvaluar={evaluarParametros} />
      )}
    </div>
  );
}
