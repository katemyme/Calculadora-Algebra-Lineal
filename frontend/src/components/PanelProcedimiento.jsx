// Línea de tiempo vertical de la eliminación: un bloque por operación
// elemental, con su notación destacada y la matriz resultante debajo.

import { ETIQUETA_PASO } from "../lib/formato.js";
import MatrizEstatica, { celdasCambiadas } from "./MatrizEstatica.jsx";

export default function PanelProcedimiento({
  matrizInicial,
  pasos,
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
          <MatrizEstatica matriz={matrizInicial} columnasPivote={columnasPivote} />
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
                columnasPivote={columnasPivote}
              />
            </div>
          </li>
        );
      })}
    </ol>
  );
}
