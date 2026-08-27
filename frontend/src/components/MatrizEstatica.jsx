// Muestra una matriz de valores ya calculados por el backend.
//
// NOTA DE CUMPLIMIENTO: no hay aritmética. Se comparan textos de fracciones
// para saber qué celdas cambiaron y se pinta cada valor tal cual llegó.

import { textoFraccion } from "../lib/formato.js";

/**
 * Devuelve un conjunto "fila,columna" con las celdas cuyo texto difiere
 * entre la matriz previa y la actual (comparación de cadenas, no de números).
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
  const pivotes = new Set(columnasPivote);

  return (
    <div className="inline-flex items-stretch gap-1 font-mono text-sm nums-tabulares">
      {/* Corchete izquierdo */}
      <span
        className="w-2 border-y-2 border-l-2 border-grafito/50"
        aria-hidden="true"
      />

      <div className="flex flex-col gap-1 px-1 py-1">
        {matriz.map((fila, indiceFila) => (
          <div key={indiceFila} className="flex gap-1">
            {fila.map((valor, indiceColumna) => {
              const esColumnaB = indiceColumna === fila.length - 1;
              const resaltada = celdasResaltadas.has(
                `${indiceFila},${indiceColumna}`
              );
              const esPivote = !esColumnaB && pivotes.has(indiceColumna);
              return (
                <span
                  key={indiceColumna}
                  className={
                    "inline-flex min-w-[3rem] justify-center rounded px-2 py-1 transition-colors " +
                    (esColumnaB
                      ? "ml-2 border-l-2 border-dashed border-grafito/40 pl-3 "
                      : "") +
                    (resaltada
                      ? "bg-pivote/15 font-semibold text-pivote "
                      : esPivote
                        ? "text-tinta ring-1 ring-inset ring-pivote/25 "
                        : "text-tinta ")
                  }
                >
                  {textoFraccion(valor)}
                </span>
              );
            })}
          </div>
        ))}
      </div>

      {/* Corchete derecho */}
      <span
        className="w-2 border-y-2 border-r-2 border-grafito/50"
        aria-hidden="true"
      />
    </div>
  );
}
