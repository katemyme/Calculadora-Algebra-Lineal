// Rejilla de entrada de la matriz aumentada [A | b].
//
// NOTA DE CUMPLIMIENTO: los únicos números que se manipulan en este archivo
// son índices de fila y de columna para mover el foco del teclado por la
// rejilla. Los coeficientes del sistema se leen del evento y se guardan
// SIEMPRE como texto; jamás se opera con ellos.

import { useRef } from "react";
import { nombreVariable } from "../lib/formato.js";

export default function MatrizAumentada({
  coeficientes, // string[m][n]
  terminos, // string[m]
  onCambiarCoeficiente,
  onCambiarTermino,
  celdaError, // { fila, columna } en base 1, o null
}) {
  // Guarda una referencia a cada <input> con clave "fila:columna".
  const referencias = useRef({});
  const registrar = (clave) => (elemento) => {
    if (elemento) referencias.current[clave] = elemento;
    else delete referencias.current[clave];
  };

  // Orden de columnas para la navegación: "0" … "n-1" y por último "b".
  const clavesColumna = [
    ...coeficientes[0].map((_, indice) => String(indice)),
    "b",
  ];
  const ultimaFila = coeficientes.length - 1;
  const ultimaColumna = clavesColumna.length - 1;

  function enfocar(fila, indiceColumna) {
    // Se limita el destino a los límites de la rejilla (coordenadas, no datos).
    const filaDestino = Math.min(Math.max(fila, 0), ultimaFila);
    const columnaDestino = Math.min(Math.max(indiceColumna, 0), ultimaColumna);
    const elemento =
      referencias.current[`${filaDestino}:${clavesColumna[columnaDestino]}`];
    if (elemento) {
      elemento.focus();
      elemento.select();
    }
  }

  function manejarTeclado(evento, fila, claveColumna) {
    const indiceColumna = clavesColumna.indexOf(claveColumna);
    const movimientos = {
      ArrowUp: [fila - 1, indiceColumna],
      ArrowDown: [fila + 1, indiceColumna],
      ArrowLeft: [fila, indiceColumna - 1],
      ArrowRight: [fila, indiceColumna + 1],
      Enter: [fila + 1, indiceColumna], // Enter baja de fila
    };
    const destino = movimientos[evento.key];
    if (destino) {
      evento.preventDefault();
      enfocar(destino[0], destino[1]);
    }
  }

  function tieneError(fila, claveColumna) {
    if (!celdaError || celdaError.fila !== fila + 1) return false;
    if (celdaError.columna == null) return true; // error de fila completa
    if (claveColumna === "b") return celdaError.columna === clavesColumna.length;
    return celdaError.columna === Number(claveColumna) + 1;
  }

  const claseCelda = (conError) =>
    "h-9 w-16 rounded-md border bg-superficie px-2 text-center font-mono text-sm " +
    "nums-tabulares transition-colors placeholder:text-grafito/40 " +
    (conError
      ? "border-inconsistente ring-2 ring-inconsistente/40"
      : "border-[var(--borde)] focus:border-pivote");

  return (
    <div className="overflow-x-auto pb-1">
      <div className="inline-block">
        {/* Encabezados: x₁ … xₙ | b */}
        <div className="mb-2 flex items-end gap-2">
          {coeficientes[0].map((_, columna) => (
            <div
              key={columna}
              className="w-16 text-center font-display text-sm text-grafito"
            >
              {nombreVariable(columna)}
            </div>
          ))}
          <div className="w-4" aria-hidden="true" />
          <div className="w-16 text-center font-display text-sm text-grafito">
            b
          </div>
        </div>

        {/* Filas de la matriz */}
        {coeficientes.map((fila, indiceFila) => (
          <div key={indiceFila} className="flex items-center gap-2 py-1">
            {fila.map((valor, columna) => (
              <input
                key={columna}
                ref={registrar(`${indiceFila}:${columna}`)}
                type="text"
                inputMode="text"
                autoComplete="off"
                spellCheck={false}
                placeholder="0"
                aria-label={`Fila ${indiceFila + 1}, ${nombreVariable(columna)}`}
                aria-invalid={tieneError(indiceFila, String(columna)) || undefined}
                value={valor}
                onChange={(evento) =>
                  onCambiarCoeficiente(indiceFila, columna, evento.target.value)
                }
                onKeyDown={(evento) =>
                  manejarTeclado(evento, indiceFila, String(columna))
                }
                className={claseCelda(tieneError(indiceFila, String(columna)))}
              />
            ))}

            {/* Barra vertical de la matriz aumentada (separación de b) */}
            <div
              className="mx-1 h-9 w-px bg-grafito/40"
              aria-hidden="true"
            />

            <input
              ref={registrar(`${indiceFila}:b`)}
              type="text"
              inputMode="text"
              autoComplete="off"
              spellCheck={false}
              placeholder="0"
              aria-label={`Fila ${indiceFila + 1}, término independiente`}
              aria-invalid={tieneError(indiceFila, "b") || undefined}
              value={terminos[indiceFila]}
              onChange={(evento) =>
                onCambiarTermino(indiceFila, evento.target.value)
              }
              onKeyDown={(evento) => manejarTeclado(evento, indiceFila, "b")}
              className={claseCelda(tieneError(indiceFila, "b"))}
            />
          </div>
        ))}
      </div>

      <p className="mt-3 text-xs text-grafito">
        Acepta enteros, decimales y fracciones (p. ej. <code>-3</code>,{" "}
        <code>2.5</code>, <code>1/3</code>). Celda vacía = 0. Navega con Tab,
        Enter y las flechas.
      </p>
    </div>
  );
}
