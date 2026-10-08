// Reducción por filas de [A | 0] (o de [A | I], indicando `columnasDerecha`),
// una operación a la vez: matriz de antes → operación → matriz de después, con
// las celdas que cambian resaltadas y la escalera de pivotes creciendo. Las
// matrices ya vienen calculadas por el backend (`pasos_detalle`); aquí solo se
// elige cuál mostrar.

import { useEffect, useState } from "react";
import { ETIQUETA_PASO } from "../../lib/formato.js";
import MatrizEstatica, { celdasCambiadas } from "../MatrizEstatica.jsx";
import { BotonControl } from "../programa3/VisualTranspuesta.jsx";

const MS_POR_PASO = 1800;

export default function ReduccionPorFilas({
  matrizInicial,
  pasos,
  columnasPivote,
  columnasDerecha = 1, // n para reducir [A | I] (Programa 5)
  aumentada = true, // false: matriz sin barra (reducción a triangular del Programa 5)
}) {
  const total = pasos.length;
  const [actual, setActual] = useState(1); // paso que se muestra (1..total)
  const [reproduciendo, setReproduciendo] = useState(false);

  useEffect(() => {
    if (!reproduciendo) return undefined;
    if (actual >= total) {
      setReproduciendo(false);
      return undefined;
    }
    const temporizador = setTimeout(() => setActual((p) => p + 1), MS_POR_PASO);
    return () => clearTimeout(temporizador);
  }, [reproduciendo, actual, total]);

  if (total === 0) {
    return (
      <p className="text-sm text-grafito">
        Ninguna operación: la matriz ya estaba en forma escalonada reducida.
      </p>
    );
  }

  function ir(numero) {
    setReproduciendo(false);
    setActual(Math.min(total, Math.max(1, numero)));
  }

  function reproducir() {
    setActual(1);
    setReproduciendo(true);
  }

  const paso = pasos[actual - 1];
  const previa = actual === 1 ? matrizInicial : pasos[actual - 2].matriz;
  const cambios = celdasCambiadas(previa, paso.matriz);
  const pivotesHastaAqui = columnasPivote.filter((c) => c <= paso.columna_pivote);

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
            {p.notacion}
          </button>
        ))}
      </div>

      <div key={actual} className="space-y-3" style={{ animation: "aparecer-paso 0.35s ease both" }}>
        <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
          <span className="font-mono text-xs text-grafito">
            Paso {actual} de {total}
          </span>
          <span className="rounded bg-pivote/10 px-2 py-0.5 font-display text-sm font-semibold text-pivote">
            {paso.notacion}
          </span>
          <span className="text-xs uppercase tracking-wide text-grafito">
            {ETIQUETA_PASO[paso.tipo]}
          </span>
        </div>

        <div className="flex flex-wrap items-center gap-x-4 gap-y-3 overflow-x-auto">
          <div className="space-y-1">
            <p className="text-xs font-semibold text-grafito">Antes</p>
            <MatrizEstatica matriz={previa} aumentada={aumentada} columnasDerecha={columnasDerecha} />
          </div>
          <div className="flex flex-col items-center text-pivote">
            <span className="font-display text-xs font-semibold">{paso.notacion}</span>
            <span className="text-2xl leading-none">⟶</span>
          </div>
          <div className="space-y-1">
            <p className="text-xs font-semibold text-grafito">Después</p>
            <MatrizEstatica
              matriz={paso.matriz}
              aumentada={aumentada}
              columnasDerecha={columnasDerecha}
              celdasResaltadas={cambios}
              columnasPivote={pivotesHastaAqui}
            />
          </div>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <BotonControl titulo="Paso anterior" onClick={() => ir(actual - 1)} disabled={actual === 1}>
          ◀
        </BotonControl>
        <BotonControl titulo="Paso siguiente" onClick={() => ir(actual + 1)} disabled={actual === total}>
          ▶
        </BotonControl>
        <BotonControl titulo="Reproducir desde el inicio" onClick={reproducir} ancho>
          {reproduciendo ? "Reproduciendo…" : "▶ Reproducir"}
        </BotonControl>
        <span className="text-xs text-grafito">Las celdas resaltadas son las que cambia la operación.</span>
      </div>
    </div>
  );
}
