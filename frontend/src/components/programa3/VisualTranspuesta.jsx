// Animación de la transposición: cada fila del origen se pinta de un color y
// aparece, con ese mismo color, como columna del destino. Los valores ya
// vienen calculados por el backend; aquí solo se decide qué pintar y cuándo.

import { useEffect, useState } from "react";
import Tex, { texNumero } from "../Tex.jsx";

// Un color por fila (máximo 8 filas).
export const COLORES_FILA = [
  "#6d3beb",
  "#2563eb",
  "#0891b2",
  "#0e9f6e",
  "#c77700",
  "#d63c4a",
  "#db2777",
  "#475569",
];

const MS_POR_FILA = 1300;

/** Entrada con subíndices LaTeX: a_{ij} para A y B, (A^{T})_{ij} para el resto. */
export function texIndices(nombre, indices) {
  return nombre === "A" || nombre === "B"
    ? `${nombre.toLowerCase()}_{${indices}}`
    : `(${nombre})_{${indices}}`;
}

/** Entrada (i, j) en base 0: a_{12} o (A^{T})_{12}. */
export function texEntrada(nombre, i, j) {
  return texIndices(nombre, `${i + 1}${j + 1}`);
}

/**
 * Matriz con corchetes y celdas coloreables.
 * estiloCelda(i, j) → { color, fuerte, vacia, borde } | null
 */
export function MatrizColor({ matriz, estiloCelda = () => null, onEntrar, onSalir }) {
  const columnas = matriz[0].length;
  return (
    <div className="relative inline-block px-2.5 py-1.5">
      <span
        aria-hidden="true"
        className="absolute inset-y-0 left-0 w-2 rounded-l-sm border-y-2 border-l-2 border-tinta/70"
      />
      <span
        aria-hidden="true"
        className="absolute inset-y-0 right-0 w-2 rounded-r-sm border-y-2 border-r-2 border-tinta/70"
      />
      <div
        className="grid gap-1"
        style={{ gridTemplateColumns: `repeat(${columnas}, minmax(2.6rem, auto))` }}
      >
        {matriz.map((fila, i) =>
          fila.map((valor, j) => {
            const estilo = estiloCelda(i, j);
            const vacia = estilo?.vacia;
            const color = estilo?.color;
            return (
              <span
                key={`${i},${j}-${vacia ? "v" : "l"}`}
                onMouseEnter={onEntrar ? () => onEntrar(i, j) : undefined}
                onMouseLeave={onSalir}
                className={
                  "flex h-10 items-center justify-center rounded-md px-1.5 text-[1.05rem] transition-colors " +
                  (vacia ? "border border-dashed border-grafito/30" : "")
                }
                style={{
                  backgroundColor: color && !vacia ? `${color}${estilo.fuerte ? "33" : "17"}` : undefined,
                  color: color && !vacia ? color : undefined,
                  fontWeight: estilo?.fuerte ? 700 : undefined,
                  boxShadow: estilo?.borde ? `0 0 0 2px ${estilo.borde}` : undefined,
                  animation: estilo?.aparece ? "aparecer-paso 0.45s ease both" : undefined,
                }}
              >
                {vacia ? "" : <Tex tex={texNumero(valor)} />}
              </span>
            );
          })
        )}
      </div>
    </div>
  );
}

/**
 * origen: { nombre (LaTeX), matriz }   destino: { nombre (LaTeX), matriz }
 * El destino se construye columna a columna: tras `movidas` pasos, las
 * primeras `movidas` filas del origen ya están escritas como columnas.
 */
export default function VisualTranspuesta({ origen, destino }) {
  const m = origen.matriz.length;
  const [movidas, setMovidas] = useState(m);
  const [reproduciendo, setReproduciendo] = useState(false);
  const [encima, setEncima] = useState(null); // { i, j } en coordenadas del origen

  useEffect(() => {
    if (!reproduciendo) return undefined;
    if (movidas >= m) {
      setReproduciendo(false);
      return undefined;
    }
    const temporizador = setTimeout(() => setMovidas((k) => k + 1), MS_POR_FILA);
    return () => clearTimeout(temporizador);
  }, [reproduciendo, movidas, m]);

  function reproducir() {
    setMovidas(0);
    setReproduciendo(true);
  }

  function mover(delta) {
    setReproduciendo(false);
    setMovidas((k) => Math.min(m, Math.max(0, k + delta)));
  }

  const activa = movidas > 0 ? movidas - 1 : null;
  const completa = movidas === m;
  const diagonal = (i, j) => i === j && completa;

  const estiloOrigen = (i, j) => {
    const borde =
      encima && encima.i === i && encima.j === j ? "var(--tinta)" : diagonal(i, j) ? "#94a3b8" : null;
    if (i >= movidas) return borde ? { borde } : null;
    return { color: COLORES_FILA[i], fuerte: i === activa && !completa, borde };
  };

  // Celda (r, c) del destino = celda (c, r) del origen.
  const estiloDestino = (r, c) => {
    const borde =
      encima && encima.i === c && encima.j === r ? "var(--tinta)" : diagonal(r, c) ? "#94a3b8" : null;
    if (c >= movidas) return { vacia: true };
    return {
      color: COLORES_FILA[c],
      fuerte: c === activa && !completa,
      aparece: c === activa && !completa,
      borde,
    };
  };

  const filaActivaTex =
    activa !== null
      ? origen.matriz[activa].map((v) => texNumero(v)).join(",\\ ")
      : "";

  let explicacion;
  if (encima) {
    const valor = texNumero(origen.matriz[encima.i][encima.j]);
    explicacion = (
      <Tex
        tex={`${texEntrada(origen.nombre, encima.i, encima.j)} = ${valor} \\;\\longrightarrow\\; ${texEntrada(destino.nombre, encima.j, encima.i)} = ${valor}`}
      />
    );
  } else if (movidas === 0) {
    explicacion = (
      <span>
        <Tex tex={destino.nombre} /> está vacía: pulse ▶ para mover la primera fila.
      </span>
    );
  } else if (completa) {
    explicacion = (
      <span>
        Regla general: <Tex tex={`${texIndices(destino.nombre, "ij")} = ${texIndices(origen.nombre, "ji")}`} />.
      </span>
    );
  } else {
    explicacion = (
      <span>
        Fila {activa + 1} de <Tex tex={origen.nombre} />:{" "}
        <Tex tex={`(${filaActivaTex})`} /> se escribe como columna {activa + 1} de{" "}
        <Tex tex={destino.nombre} />.
      </span>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-x-3 gap-y-2 overflow-x-auto">
        <div className="flex items-center gap-2">
          <Tex tex={`${origen.nombre} =`} className="text-lg" />
          <MatrizColor
            matriz={origen.matriz}
            estiloCelda={estiloOrigen}
            onEntrar={(i, j) => setEncima({ i, j })}
            onSalir={() => setEncima(null)}
          />
        </div>
        <Tex tex={"\\xrightarrow{\\ \\text{transponer}\\ }"} className="text-lg text-grafito" />
        <div className="flex items-center gap-2">
          <Tex tex={`${destino.nombre} =`} className="text-lg" />
          <MatrizColor
            matriz={destino.matriz}
            estiloCelda={estiloDestino}
            onEntrar={(r, c) => setEncima({ i: c, j: r })}
            onSalir={() => setEncima(null)}
          />
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <BotonControl titulo="Paso anterior" onClick={() => mover(-1)} disabled={movidas === 0}>
          ◀
        </BotonControl>
        <BotonControl titulo="Paso siguiente" onClick={() => mover(1)} disabled={completa}>
          ▶
        </BotonControl>
        <BotonControl titulo="Reproducir desde el inicio" onClick={reproducir} ancho>
          {reproduciendo ? "Reproduciendo…" : "▶ Reproducir"}
        </BotonControl>
        <span className="text-xs text-grafito">
          Filas movidas: {movidas} de {m}
        </span>
      </div>

      <p className="min-h-[1.75rem] w-0 min-w-full text-sm text-tinta">{explicacion}</p>
    </div>
  );
}

export function BotonControl({ titulo, onClick, disabled, ancho, children }) {
  return (
    <button
      type="button"
      title={titulo}
      aria-label={titulo}
      onClick={onClick}
      disabled={disabled}
      className={
        "h-8 rounded-md border border-[var(--borde)] bg-white text-sm font-semibold text-grafito " +
        "transition-colors hover:border-pivote hover:text-pivote disabled:opacity-40 " +
        (ancho ? "px-3" : "w-8")
      }
    >
      {children}
    </button>
  );
}
