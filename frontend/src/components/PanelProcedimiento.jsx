// Línea de tiempo vertical de la eliminación: un bloque por operación
// elemental, con su notación destacada y la matriz resultante debajo. La
// escalera de pivotes se redibuja conforme avanzan los pasos.

import { ETIQUETA_PASO } from "../lib/formato.js";
import MatrizEstatica, { celdasCambiadas } from "./MatrizEstatica.jsx";

// Pivotes ya fijados hasta un paso: los de columna ≤ la columna que trabaja el
// paso (la eliminación avanza siempre de izquierda a derecha).
function pivotesHastaColumna(columnasPivote, columnaActual) {
  return columnasPivote.filter((columna) => columna <= columnaActual);
}

export default function PanelProcedimiento({
  matrizInicial,
  pasos,
  matrizReducida,
  columnasPivote,
}) {
  if (pasos.length === 0) {
    return (
      <div>
        <p className="text-sm text-grafito">
          La matriz ya estaba en forma escalonada reducida: no se necesitó
          ninguna operación por fila.
        </p>
        <div className="mt-3 overflow-x-auto">
          <MatrizEstatica
            matriz={matrizReducida}
            columnasPivote={columnasPivote}
          />
        </div>
      </div>
    );
  }

  return (
    <ol className="space-y-6">
      <li>
        <p className="font-display text-sm font-semibold text-grafito">
          Matriz aumentada inicial
        </p>
        <div className="mt-2 overflow-x-auto">
          <MatrizEstatica matriz={matrizInicial} />
        </div>
      </li>

      {pasos.map((paso, indice) => {
        const matrizPrevia =
          indice === 0 ? matrizInicial : pasos[indice - 1].matriz;
        const cambios = celdasCambiadas(matrizPrevia, paso.matriz);

        return (
          <li
            key={paso.numero}
            className="relative border-l-2 border-[var(--borde)] pl-6"
            style={{
              animation: "aparecer-paso 0.35s ease both",
              animationDelay: `${indice * 35}ms`,
            }}
          >
            <span
              className="absolute -left-[9px] top-1 h-4 w-4 rounded-full border-2 border-pivote bg-superficie"
              aria-hidden="true"
            />

            <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
              <span className="font-mono text-xs text-grafito">
                Paso {paso.numero}
              </span>
              <span className="rounded bg-pivote/10 px-2 py-0.5 font-display text-sm font-semibold text-pivote">
                {paso.notacion}
              </span>
              <span className="text-xs uppercase tracking-wide text-grafito">
                {ETIQUETA_PASO[paso.tipo]}
              </span>
            </div>

            <p className="mt-1 text-sm text-grafito">{paso.descripcion}</p>

            <div className="mt-3 overflow-x-auto">
              <MatrizEstatica
                matriz={paso.matriz}
                celdasResaltadas={cambios}
                columnasPivote={pivotesHastaColumna(
                  columnasPivote,
                  paso.columna_pivote
                )}
              />
            </div>
          </li>
        );
      })}

      <li className="relative border-l-2 border-pivote pl-6">
        <span
          className="absolute -left-[9px] top-1 h-4 w-4 rounded-full border-2 border-pivote bg-pivote"
          aria-hidden="true"
        />
        <p className="font-display text-sm font-semibold text-pivote">
          Forma escalonada reducida por filas
        </p>
        <div className="mt-2 overflow-x-auto">
          <MatrizEstatica
            matriz={matrizReducida}
            columnasPivote={columnasPivote}
          />
        </div>
      </li>
    </ol>
  );
}
