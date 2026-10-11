// PROGRAMA 6 – Paso a paso de la reducción A → U.
//
// Muestra un reemplazo de fila a la vez: cómo se calcula su multiplicador, la
// matriz antes y después de la operación y en qué posición de L queda guardado.
// Todo viene ya calculado por el backend (`pasos`); aquí solo se elige cuál ver.

import { useState } from "react";
import MatrizEstatica, { celdasCambiadas } from "../MatrizEstatica.jsx";
import { BotonControl } from "../programa3/VisualTranspuesta.jsx";

export default function PasosFactorizacion({ matrizInicial, pasos }) {
  const total = pasos.length;
  const [actual, setActual] = useState(1); // paso que se muestra (1..total)

  const ir = (numero) => setActual(Math.min(total, Math.max(1, numero)));

  const paso = pasos[actual - 1];
  const previa = actual === 1 ? matrizInicial : pasos[actual - 2].U;
  const cambios = celdasCambiadas(previa, paso.U);
  const celdaPivote = new Set([`${paso.fila_pivote},${paso.columna}`]);
  const celdaMultiplicador = new Set([`${paso.fila},${paso.fila_pivote}`]);

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-1.5">
        {pasos.map((p, indice) => (
          <button
            key={indice}
            type="button"
            onClick={() => ir(indice + 1)}
            className={
              "rounded-md border px-2 py-1 font-display text-xs font-semibold transition-colors " +
              (indice + 1 === actual
                ? "border-pivote bg-pivote text-white"
                : indice + 1 < actual
                  ? "border-pivote/40 bg-pivote/10 text-pivote"
                  : "border-[var(--borde)] bg-white text-grafito hover:border-pivote")
            }
          >
            {p.numero}. {p.operacion}
          </button>
        ))}
      </div>

      <div key={actual} className="space-y-4" style={{ animation: "aparecer-paso 0.35s ease both" }}>
        <p className="font-mono text-xs text-grafito">
          Paso {actual} de {total}
        </p>

        <div className="lu-subpaso">
          <span className="lu-subpaso-letra">a</span>
          <div className="space-y-1">
            <p className="text-sm text-tinta">
              <strong>Calcular el multiplicador.</strong> Para anular la entrada de la fila{" "}
              {paso.fila + 1} se divide esa entrada entre el pivote de la fila {paso.fila_pivote + 1}:
            </p>
            <p className="font-mono text-sm font-semibold text-pivote">
              {paso.cuenta_multiplicador}
            </p>
          </div>
        </div>

        <div className="lu-subpaso">
          <span className="lu-subpaso-letra">b</span>
          <div className="min-w-0 space-y-2">
            <p className="text-sm text-tinta">
              <strong>Reemplazar la fila.</strong> Se aplica{" "}
              <span className="font-mono font-semibold text-pivote">{paso.operacion}</span> y la
              entrada queda en 0:
            </p>
            <div className="flex flex-wrap items-center gap-x-4 gap-y-3 overflow-x-auto">
              <div className="space-y-1">
                <p className="text-xs font-semibold text-grafito">Antes (pivote resaltado)</p>
                <MatrizEstatica matriz={previa} aumentada={false} celdasResaltadas={celdaPivote} />
              </div>
              <div className="flex flex-col items-center text-pivote">
                <span className="font-display text-xs font-semibold">{paso.operacion}</span>
                <span className="text-2xl leading-none">⟶</span>
              </div>
              <div className="space-y-1">
                <p className="text-xs font-semibold text-grafito">Después (fila modificada)</p>
                <MatrizEstatica matriz={paso.U} aumentada={false} celdasResaltadas={cambios} />
              </div>
            </div>
          </div>
        </div>

        <div className="lu-subpaso">
          <span className="lu-subpaso-letra">c</span>
          <div className="min-w-0 space-y-2">
            <p className="text-sm text-tinta">
              <strong>Guardar el multiplicador en L.</strong> {paso.nombre_multiplicador} ocupa la
              fila {paso.fila + 1}, columna {paso.fila_pivote + 1} de L:
            </p>
            <div className="flex overflow-x-auto">
              <div className="space-y-1">
                <p className="text-xs font-semibold text-grafito">L hasta este paso</p>
                <MatrizEstatica
                  matriz={paso.L}
                  aumentada={false}
                  celdasResaltadas={celdaMultiplicador}
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <BotonControl titulo="Paso anterior" onClick={() => ir(actual - 1)} disabled={actual === 1}>
          ◀
        </BotonControl>
        <BotonControl
          titulo="Paso siguiente"
          onClick={() => ir(actual + 1)}
          disabled={actual === total}
        >
          ▶
        </BotonControl>
        <span className="text-xs text-grafito">
          Use las flechas o toque una operación para ver cada paso.
        </span>
      </div>
    </div>
  );
}
