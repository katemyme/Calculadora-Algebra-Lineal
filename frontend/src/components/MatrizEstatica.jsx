// Muestra una matriz de valores ya calculados por el backend, con:
//  - corchetes dibujados como trazos SVG reales (no caracteres de texto),
//  - la barra vertical de la matriz aumentada,
//  - la "escalera de pivotes": una línea escalonada que marca dónde cae cada
//    pivote, la representación literal de la forma escalonada.
//
// NOTA DE CUMPLIMIENTO: no hay aritmética sobre el sistema. Se comparan textos
// de fracciones para saber qué celdas cambiaron y se pinta cada valor tal cual
// llegó; los únicos números que se calculan son coordenadas de dibujo (píxeles).

import { textoFraccion } from "../lib/formato.js";

// Geometría del dibujo (en píxeles).
const ANCHO_CELDA = 54;
const ALTO_CELDA = 38;
const SEPARACION_AUMENTADA = 18; // hueco antes de la columna b
const RELLENO_X = 12;
const RELLENO_Y = 10;
const BRAZO_CORCHETE = 9;

/**
 * Conjunto "fila,columna" con las celdas cuyo texto difiere entre la matriz
 * previa y la actual (comparación de cadenas, no de números).
 */
export function celdasCambiadas(matrizPrevia, matrizActual) {
  const cambios = new Set();
  matrizActual.forEach((fila, indiceFila) => {
    fila.forEach((valor, indiceColumna) => {
      const anterior = matrizPrevia[indiceFila]?.[indiceColumna];
      if (!anterior || anterior.fraccion !== valor.fraccion) {
        cambios.add(`${indiceFila},${indiceColumna}`);
      }
    });
  });
  return cambios;
}

export default function MatrizEstatica({
  matriz,
  celdasResaltadas = new Set(),
  columnasPivote = [],
}) {
  const filas = matriz.length;
  const columnas = matriz[0].length;
  const columnasCoef = columnas - 1; // la última columna es b

  const anchoContenido =
    columnasCoef * ANCHO_CELDA + SEPARACION_AUMENTADA + ANCHO_CELDA;
  const altoContenido = filas * ALTO_CELDA;
  const alturaCorchete = altoContenido + RELLENO_Y * 2;

  // x del borde izquierdo de una columna (los coeficientes van pegados; la
  // columna b va tras el hueco de la matriz aumentada).
  const xBordeColumna = (columna) =>
    columna < columnasCoef
      ? columna * ANCHO_CELDA
      : columnasCoef * ANCHO_CELDA + SEPARACION_AUMENTADA;

  // Camino de la escalera: desde la esquina superior izquierda, baja un peldaño
  // por cada pivote (pivote i está en la fila i, columna columnasPivote[i]).
  const caminoEscalera = () => {
    if (columnasPivote.length === 0) return "";
    let camino = "M 0 0";
    columnasPivote.forEach((columna, indice) => {
      const x = columna * ANCHO_CELDA;
      camino += ` L ${x} ${indice * ALTO_CELDA} L ${x} ${(indice + 1) * ALTO_CELDA}`;
    });
    // Pequeño saliente de una celda bajo el último pivote (sin invadir la
    // columna b).
    const ultimaColumna = columnasPivote[columnasPivote.length - 1];
    const xSaliente = Math.min(
      (ultimaColumna + 1) * ANCHO_CELDA,
      columnasCoef * ANCHO_CELDA
    );
    camino += ` L ${xSaliente} ${columnasPivote.length * ALTO_CELDA}`;
    return camino;
  };

  const plantillaColumnas =
    `repeat(${columnasCoef}, ${ANCHO_CELDA}px) ` +
    `${SEPARACION_AUMENTADA}px ${ANCHO_CELDA}px`;

  return (
    <div className="inline-flex select-none items-stretch font-mono text-sm nums-tabulares">
      {/* Corchete izquierdo: [ */}
      <svg
        width={BRAZO_CORCHETE}
        height={alturaCorchete}
        className="flex-shrink-0 text-grafito/70"
        aria-hidden="true"
      >
        <path
          d={`M ${BRAZO_CORCHETE} 0 L 0 0 L 0 ${alturaCorchete} L ${BRAZO_CORCHETE} ${alturaCorchete}`}
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
        />
      </svg>

      <div
        className="relative"
        style={{ padding: `${RELLENO_Y}px ${RELLENO_X}px` }}
      >
        {/* Rejilla de valores */}
        <div
          className="grid"
          style={{
            gridTemplateColumns: plantillaColumnas,
            gridTemplateRows: `repeat(${filas}, ${ALTO_CELDA}px)`,
          }}
        >
          {matriz.map((fila, indiceFila) => (
            <div key={indiceFila} className="contents">
              {fila.slice(0, columnasCoef).map((valor, columna) => (
                <Celda
                  key={columna}
                  valor={valor}
                  resaltada={celdasResaltadas.has(`${indiceFila},${columna}`)}
                  esPivote={columnasPivote.includes(columna)}
                />
              ))}
              <div aria-hidden="true" />
              <Celda
                valor={fila[columnasCoef]}
                resaltada={celdasResaltadas.has(`${indiceFila},${columnasCoef}`)}
              />
            </div>
          ))}
        </div>

        {/* Capa de dibujo: barra aumentada + escalera de pivotes */}
        <svg
          className="pointer-events-none absolute"
          style={{
            top: RELLENO_Y,
            left: RELLENO_X,
            width: anchoContenido,
            height: altoContenido,
          }}
          aria-hidden="true"
        >
          {/* Barra vertical de la matriz aumentada */}
          <line
            x1={xBordeColumna(columnasCoef) - SEPARACION_AUMENTADA / 2}
            y1="0"
            x2={xBordeColumna(columnasCoef) - SEPARACION_AUMENTADA / 2}
            y2={altoContenido}
            className="text-grafito/45"
            stroke="currentColor"
            strokeWidth="1"
            strokeDasharray="3 3"
          />

          {columnasPivote.length > 0 && (
            <>
              <path
                d={caminoEscalera()}
                className="text-pivote"
                fill="none"
                stroke="currentColor"
                strokeWidth="2.5"
                strokeLinejoin="round"
                strokeLinecap="round"
                pathLength="1"
                style={{
                  strokeDasharray: 1,
                  animation: "dibujar-escalera 0.6s ease forwards",
                }}
              />
              {columnasPivote.map((columna, indice) => (
                <circle
                  key={indice}
                  cx={columna * ANCHO_CELDA}
                  cy={indice * ALTO_CELDA}
                  r="3"
                  className="fill-current text-pivote"
                />
              ))}
            </>
          )}
        </svg>
      </div>

      {/* Corchete derecho: ] */}
      <svg
        width={BRAZO_CORCHETE}
        height={alturaCorchete}
        className="flex-shrink-0 text-grafito/70"
        aria-hidden="true"
      >
        <path
          d={`M 0 0 L ${BRAZO_CORCHETE} 0 L ${BRAZO_CORCHETE} ${alturaCorchete} L 0 ${alturaCorchete}`}
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
        />
      </svg>
    </div>
  );
}

function Celda({ valor, resaltada, esPivote }) {
  return (
    <span
      className={
        "flex items-center justify-center rounded transition-colors " +
        (resaltada
          ? "bg-pivote/15 font-semibold text-pivote"
          : esPivote
            ? "text-tinta ring-1 ring-inset ring-pivote/25"
            : "text-tinta")
      }
      style={resaltada ? { animation: "resaltar-celda 0.8s ease" } : undefined}
    >
      {textoFraccion(valor)}
    </span>
  );
}
