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
    vectores: [
      ["1", "0", "0"],
      ["0", "1", "0"],
      ["0", "0", "1"],
    ],
  },
  {
    nombre: "Dependientes",
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
  {
    nombre: "Con vector 0",
    vectores: [
      ["1", "2"],
      ["0", "0"],
    ],
  },
];

/**
 * Convierte los vectores del caso de prueba
 * en una rejilla n × k.
 *
 * Cada columna representa un vector.
 */
function rejillaDesdeCaso(caso) {
  const n = caso.vectores[0].length;

  return Array.from(
    { length: n },
    (_, i) => caso.vectores.map((v) => v[i])
  );
}

export default function SeccionIndependencia() {
  // Rejilla n filas × k columnas.
  // Inicia con la base canónica de R³.
  const [rejilla, setRejilla] = useState(
    rejillaDesdeCaso(CASOS[0])
  );

  const {
    resultado,
    error,
    cargando,
    ejecutar,
    limpiar,
  } = useOperacion();

  // Número de filas = dimensión de los vectores.
  const n = rejilla.length;

  // Número de columnas = cantidad de vectores.
  const k = rejilla[0].length;

  // Encabezados v₁, v₂, v₃, ...
  const encabezados = Array.from(
    { length: k },
    (_, j) => `v${subindice(j + 1)}`
  );

  /**
   * Cambia la dimensión n o la cantidad de vectores k.
   * También elimina cualquier resultado anterior.
   */
  function redimensionar(nuevoN, nuevoK) {
    setRejilla(
      redimensionarRejilla(
        rejilla,
        nuevoN,
        nuevoK
      )
    );

    limpiar();
  }

  /**
   * Obtiene cada columna de la matriz como un vector.
   */
  function vectoresActuales() {
    return Array.from(
      { length: k },
      (_, j) =>
        rejilla.map((fila) => fila[j])
    );
  }

  /**
   * LIMPIAR TODO
   *
   * Mantiene las dimensiones actuales n y k,
   * pero borra todos los valores de la matriz
   * y elimina la solución anterior.
   */
  function limpiarTodo() {
    const nuevaRejilla = Array.from(
      { length: n },
      () =>
        Array.from(
          { length: k },
          () => ""
        )
    );

    // Borra los valores escritos.
    setRejilla(nuevaRejilla);

    // Borra resultado y errores.
    limpiar();
  }

  /**
   * Envía los vectores al backend
   * para analizar independencia lineal.
   */
  function calcular() {
    ejecutar(() =>
      programa3.independencia({
        vectores: vectoresActuales(),
      })
    );
  }

  /**
   * Evalúa un valor elegido por el usuario
   * para los parámetros de la solución general.
   */
  async function evaluarParametros(valoresParametros) {
    const datos = await programa3.independencia({
      vectores: vectoresActuales(),
      valores_parametros: valoresParametros,
    });

    return datos.evaluacion_parametros;
  }

  /**
   * Si existe un error en una celda,
   * el backend indica fila y columna.
   */
  let celdaError = null;

  if (
    error instanceof ErrorDeCalculo &&
    error.campo === "vectores" &&
    error.fila
  ) {
    celdaError = {
      fila: error.fila,
      columna: error.columna,
    };
  }

  return (
    <div className="space-y-6">

      {/* =====================================================
          CONFIGURACIÓN DE DIMENSIONES Y CASOS DE PRUEBA
         ===================================================== */}

      <div className="flex flex-wrap items-center justify-between gap-3">

        {/* Dimensión n y cantidad de vectores k */}
        <div className="flex flex-wrap gap-x-8 gap-y-3">

          <SelectorDimension
            id="indep-n"
            etiqueta="Dimensión n"
            valor={n}
            minimo={DIMENSION_MINIMA}
            maximo={DIMENSION_MAXIMA}
            onCambiar={(nuevo) =>
              redimensionar(nuevo, k)
            }
          />

          <SelectorDimension
            id="indep-k"
            etiqueta="Vectores k"
            valor={k}
            minimo={DIMENSION_MINIMA}
            maximo={DIMENSION_MAXIMA}
            onCambiar={(nuevo) =>
              redimensionar(n, nuevo)
            }
          />

        </div>

        {/* Casos rápidos + botón limpiar */}
        <div className="flex flex-wrap gap-2">

          {CASOS.map((caso) => (
            <Boton
              key={caso.nombre}
              variante="secundario"
              className="text-xs"
              onClick={() => {
                setRejilla(
                  rejillaDesdeCaso(caso)
                );

                limpiar();
              }}
            >
              {caso.nombre}
            </Boton>
          ))}

          {/* NUEVO BOTÓN */}
          <Boton
            variante="secundario"
            className="text-xs"
            onClick={limpiarTodo}
          >
            Limpiar
          </Boton>

        </div>
      </div>

      {/* =====================================================
          FÓRMULA
         ===================================================== */}

      <div
        className="math-formula-strip"
        aria-hidden="true"
      >
        <span>
          x₁·v₁ + x₂·v₂ + … + xₖ·vₖ = 0
        </span>

        <span>
          rango = k ⇒ independientes
        </span>

        <span>
          rango &lt; k ⇒ dependientes
        </span>
      </div>

      {/* =====================================================
          MATRIZ DE VECTORES
         ===================================================== */}

      <div className="p3-lienzo">

        <EditorMatriz
          etiqueta="Vectores"
          valores={rejilla}
          encabezados={encabezados}
          celdaError={celdaError}
          onCambiar={(i, j, texto) => {

            setRejilla(
              cambiarCelda(
                rejilla,
                i,
                j,
                texto
              )
            );

            // Si el usuario cambia algún número,
            // se elimina la solución anterior.
            limpiar();
          }}
        />

        <p className="max-w-xs text-xs text-grafito">

          Cada <strong>columna</strong> es un
          vector de ℝ<sup>{n}</sup>.

          {" "}

          Se resuelve el sistema{" "}
          <strong>homogéneo</strong>{" "}
          [v₁ … v<sub>k</sub> | 0].

          {" "}

          Celda vacía = 0.

        </p>

      </div>

      {/* =====================================================
          BOTÓN CALCULAR
         ===================================================== */}

      <Boton
        onClick={calcular}
        disabled={cargando}
      >
        {cargando
          ? "Analizando…"
          : "¿Son linealmente independientes?"}
      </Boton>

      {/* =====================================================
          RESULTADOS
         ===================================================== */}

      {cargando && (
        <Cargando texto="Reduciendo [v₁ … vₖ | 0]…" />
      )}

      <AvisoError error={error} />

      {resultado && (
        <ResultadoIndependencia
          resultado={resultado}
          onEvaluar={evaluarParametros}
        />
      )}

    </div>
  );
}