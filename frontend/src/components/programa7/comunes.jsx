// Piezas compartidas por las pestañas de Métodos Numéricos (Programa 7).
//
// NOTA DE CUMPLIMIENTO: aquí solo se da formato a los números que devuelve el
// backend para mostrarlos. Ningún cálculo matemático se hace en JavaScript.

import Boton from "../ui/Boton.jsx";

export { CampoTexto } from "../transformaciones/comunes.jsx";
export { AvisoError, Cargando, useOperacion } from "../programa3/comunes.jsx";

/** Número para mostrar: "—" si no hay valor; notación científica si es muy grande o pequeño. */
export function formatear(valor, cifras = 10) {
  if (valor === null || valor === undefined) return "—";
  if (valor === 0) return "0";
  const absoluto = Math.abs(valor);
  if (absoluto < 1e-4 || absoluto >= 1e10) return valor.toExponential(Math.min(cifras - 1, 6));
  return String(Number(valor.toPrecision(cifras)));
}

const VARIANTES = {
  ok: { clase: "math-solution-ok", icono: "✓", color: "var(--determinado, #0e9f6e)" },
  error: { clase: "math-solution-error", icono: "✗", color: "var(--inconsistente)" },
  aviso: { clase: "math-solution-infinite", icono: "!", color: "var(--indeterminado)" },
};

/** Recuadro de conclusión (ok / error / aviso) con título y texto. */
export function Banner({ variante = "ok", titulo, children }) {
  const { clase, icono, color } = VARIANTES[variante];
  return (
    <div
      role={variante === "error" ? "alert" : "status"}
      className={`math-solution-banner ${clase}`}
      style={{ animation: "aparecer-paso 0.3s ease both" }}
    >
      <div className="math-solution-icon" style={{ color }}>{icono}</div>
      <div className="min-w-0">
        <p className="font-display text-lg font-bold" style={{ color }}>{titulo}</p>
        <div className="mt-1 text-sm text-tinta">{children}</div>
      </div>
    </div>
  );
}

/** Lista de avisos visibles (p. ej. "se convirtió ^ en **"). */
export function Avisos({ avisos }) {
  if (!avisos || avisos.length === 0) return null;
  return (
    <div className="space-y-2">
      {avisos.map((aviso) => (
        <p key={aviso} className="math-note">⚠ {aviso}</p>
      ))}
    </div>
  );
}

/** Tarjeta pequeña con una etiqueta y un valor. */
export function Dato({ etiqueta, valor, detalle, destacado = false }) {
  return (
    <div className="rounded-xl border border-[var(--borde)] bg-white px-4 py-3">
      <p className="text-xs font-semibold uppercase tracking-wide text-grafito">{etiqueta}</p>
      <p className={`mt-1 break-all font-mono ${destacado ? "text-lg font-bold text-pivote" : "text-base text-tinta"}`}>
        {valor}
      </p>
      {detalle && <p className="mt-1 text-xs text-grafito">{detalle}</p>}
    </div>
  );
}

/** Botones de ejemplos precargados más "Limpiar". */
export function BotonesEjemplo({ ejemplos, etiqueta, onElegir, onLimpiar }) {
  return (
    <div className="flex flex-wrap gap-2">
      {ejemplos.map((ejemplo, indice) => (
        <Boton key={indice} variante="secundario" className="text-xs" onClick={() => onElegir(ejemplo)}>
          {etiqueta(ejemplo)}
        </Boton>
      ))}
      {onLimpiar && (
        <Boton variante="fantasma" className="text-xs" onClick={onLimpiar}>
          Limpiar
        </Boton>
      )}
    </div>
  );
}

/** Texto de ayuda con las funciones que admite el parser seguro del backend. */
export const AYUDA_FUNCION = (
  <>
    Use <strong>x</strong>, números, <code>+ - * / **</code>, paréntesis, <code>pi</code>, <code>e</code> y{" "}
    <code>sin cos tan asin acos atan sinh cosh tanh exp log ln log10 sqrt abs</code>. Multiplique con{" "}
    <code>*</code> (2*x). Si escribe <code>^</code>, se convierte en <code>**</code> y se le avisa.
  </>
);
