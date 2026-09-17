// Piezas compartidas por las secciones del Programa 3.
//
// NOTA DE CUMPLIMIENTO: aquí solo se guardan textos y se manejan índices de
// la rejilla. Todas las operaciones algebraicas las hace el backend
// ("Programa 3_GrupoX.py").

import { useRef, useState } from "react";
import { ErrorDeCalculo, ErrorDeServidor } from "../../lib/api.js";
import MatrizEstatica from "../MatrizEstatica.jsx";

export const DIMENSION_MINIMA = 1;
export const DIMENSION_MAXIMA = 8;

/** Rejilla de texto filas×columnas, conservando lo que siga cabiendo. */
export function redimensionarRejilla(previa, filas, columnas) {
  return Array.from({ length: filas }, (_, i) =>
    Array.from({ length: columnas }, (_, j) => previa[i]?.[j] ?? "")
  );
}

/** Vector de texto de longitud n, conservando lo que siga cabiendo. */
export function redimensionarVector(previo, n) {
  return Array.from({ length: n }, (_, i) => previo[i] ?? "");
}

/** Cambia una celda de una rejilla de texto (copia inmutable). */
export function cambiarCelda(rejilla, fila, columna, valor) {
  return rejilla.map((f, i) =>
    i === fila ? f.map((v, j) => (j === columna ? valor : v)) : f
  );
}

/** Estado común de una llamada al backend: resultado, error y carga. */
export function useOperacion() {
  const [resultado, setResultado] = useState(null);
  const [error, setError] = useState(null);
  const [cargando, setCargando] = useState(false);

  async function ejecutar(llamada) {
    setCargando(true);
    setError(null);
    setResultado(null);
    try {
      setResultado(await llamada());
    } catch (excepcion) {
      setError(excepcion);
    } finally {
      setCargando(false);
    }
  }

  function limpiar() {
    setResultado(null);
    setError(null);
  }

  return { resultado, error, cargando, ejecutar, limpiar };
}

/** Celda con error para un campo concreto ("A", "b", ...), o null. */
export function celdaConError(error, campo) {
  if (!(error instanceof ErrorDeCalculo) || error.campo !== campo) return null;
  return { fila: error.fila, columna: error.columna };
}

/**
 * Rejilla editable con corchetes. `encabezados` nombra cada columna y
 * `separarUltima` dibuja la barra de una matriz aumentada antes de la última.
 */
export function EditorMatriz({
  valores,
  onCambiar,
  encabezados = null,
  separarUltima = false,
  celdaError = null,
  etiqueta = "",
  compacta = false,
}) {
  const referencias = useRef({});
  const filas = valores.length;
  const columnas = valores[0].length;

  function enfocar(fila, columna) {
    const destino =
      referencias.current[
        `${Math.min(Math.max(fila, 0), filas - 1)}:${Math.min(
          Math.max(columna, 0),
          columnas - 1
        )}`
      ];
    if (destino) {
      destino.focus();
      destino.select();
    }
  }

  function manejarTeclado(evento, fila, columna) {
    const movimientos = {
      ArrowUp: [fila - 1, columna],
      ArrowDown: [fila + 1, columna],
      ArrowLeft: [fila, columna - 1],
      ArrowRight: [fila, columna + 1],
      Enter: [fila + 1, columna],
    };
    const destino = movimientos[evento.key];
    if (destino) {
      evento.preventDefault();
      enfocar(destino[0], destino[1]);
    }
  }

  const tieneError = (fila, columna) =>
    Boolean(celdaError) &&
    celdaError.fila === fila + 1 &&
    (celdaError.columna == null || celdaError.columna === columna + 1);

  const ancho = compacta ? "w-14" : "w-16";

  return (
    <div className="inline-flex flex-col">
      {encabezados && (
        <div className="mb-1 flex gap-2 px-[14px]">
          {encabezados.map((texto, columna) => (
            <div key={columna} className="flex items-center gap-2">
              {separarUltima && columna === columnas - 1 && (
                <div className="w-px" aria-hidden="true" />
              )}
              <div
                className={`${ancho} text-center font-display text-sm text-grafito`}
              >
                {texto}
              </div>
            </div>
          ))}
        </div>
      )}
      <div className="p3-corchetes">
        {valores.map((fila, i) => (
          <div key={i} className="flex items-center gap-2 py-1">
            {fila.map((valor, j) => (
              <div key={j} className="flex items-center gap-2">
                {separarUltima && j === columnas - 1 && (
                  <div className="h-9 w-px bg-grafito/40" aria-hidden="true" />
                )}
                <input
                  ref={(elemento) => {
                    if (elemento) referencias.current[`${i}:${j}`] = elemento;
                    else delete referencias.current[`${i}:${j}`];
                  }}
                  type="text"
                  autoComplete="off"
                  spellCheck={false}
                  placeholder="0"
                  aria-label={`${etiqueta} fila ${i + 1}, columna ${j + 1}`}
                  aria-invalid={tieneError(i, j) || undefined}
                  value={valor}
                  onChange={(evento) => onCambiar(i, j, evento.target.value)}
                  onKeyDown={(evento) => manejarTeclado(evento, i, j)}
                  className={
                    `h-9 ${ancho} rounded-md border bg-superficie px-2 text-center font-mono text-sm ` +
                    "nums-tabulares transition-colors placeholder:text-grafito/40 " +
                    (tieneError(i, j)
                      ? "border-inconsistente ring-2 ring-inconsistente/40"
                      : "border-[var(--borde)] focus:border-pivote")
                  }
                />
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

/** Bloque "Nombre = [matriz]" con el orden m×n debajo. */
export function BloqueMatriz({ nombre, orden, children }) {
  return (
    <div className="flex flex-col items-center gap-1">
      <div className="flex items-center gap-2">
        {nombre && (
          <span className="font-display text-lg font-bold text-tinta">{nombre}</span>
        )}
        {children}
      </div>
      {orden && <span className="font-mono text-xs text-grafito">{orden}</span>}
    </div>
  );
}

/** Vector serializado dibujado como matriz columna n×1. */
export function VectorColumna({ vector, ...props }) {
  return (
    <MatrizEstatica
      matriz={vector.map((valor) => [valor])}
      aumentada={false}
      {...props}
    />
  );
}

/** Texto (a, b, c) a partir de un vector serializado. */
export function textoVector(vector) {
  return `(${vector.map((valor) => valor.fraccion).join(", ")})`;
}

/** Operador grande entre matrices (+, −, ·, =). */
export function Operador({ children }) {
  return (
    <span className="px-1 font-display text-2xl font-semibold text-grafito">
      {children}
    </span>
  );
}

/** Botones segmentados para elegir la operación. */
export function SelectorOperacion({ opciones, activa, onCambiar }) {
  return (
    <div className="inline-flex flex-wrap gap-1 rounded-xl border border-[var(--borde)] bg-papel/60 p-1">
      {opciones.map((opcion) => (
        <button
          key={opcion.id}
          type="button"
          aria-pressed={opcion.id === activa}
          onClick={() => onCambiar(opcion.id)}
          className={
            "rounded-lg px-3 py-1.5 font-mono text-sm font-semibold transition-colors " +
            (opcion.id === activa
              ? "bg-pivote text-white shadow"
              : "text-grafito hover:bg-white hover:text-pivote")
          }
        >
          {opcion.etiqueta}
        </button>
      ))}
    </div>
  );
}

/** Caja de error del backend (validación o servidor caído). */
export function AvisoError({ error }) {
  if (!error) return null;
  const titulo =
    error instanceof ErrorDeServidor
      ? "Servidor no disponible"
      : "No se puede realizar la operación";
  return (
    <div
      role="alert"
      className="math-solution-banner math-solution-error"
      style={{ animation: "aparecer-paso 0.3s ease both" }}
    >
      <div className="math-solution-icon" style={{ color: "var(--inconsistente)" }}>✗</div>
      <div>
        <p className="font-display text-lg font-bold text-inconsistente">{titulo}</p>
        <p className="mt-1 text-sm text-tinta">{error.message}</p>
      </div>
    </div>
  );
}

/** Indicador de carga. */
export function Cargando({ texto = "Calculando…" }) {
  return (
    <div className="flex items-center gap-3 text-grafito">
      <span className="math-loader" aria-hidden="true" />
      {texto}
    </div>
  );
}

/** Panel de resultado con cabecera y fórmula. */
export function TarjetaResultado({ titulo, formula, children }) {
  return (
    <div
      className="overflow-hidden rounded-[var(--radio)] border border-[var(--borde)] bg-white"
      style={{ animation: "aparecer-paso 0.35s ease both" }}
    >
      <div className="math-results-header flex flex-wrap items-center justify-between gap-2 px-5 py-3">
        <p className="font-display text-lg font-bold">{titulo}</p>
        {formula && <span className="math-result-badge">{formula}</span>}
      </div>
      <div className="p-5">{children}</div>
    </div>
  );
}
