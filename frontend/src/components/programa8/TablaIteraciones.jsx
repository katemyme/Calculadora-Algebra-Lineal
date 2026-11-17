// Muestra los resultados, el estado final, el residuo y la tabla de iteraciones
// de un método iterativo (Jacobi o Gauss-Seidel).

import Panel from "../ui/Panel.jsx";

const SUBINDICES = ["₁", "₂", "₃", "₄", "₅", "₆", "₇", "₈"];

function subindice(i) {
  return SUBINDICES[i] ?? `_${i + 1}`;
}

export function formatearNumero(valor, decimales = 6) {
  if (valor === null || valor === undefined || Number.isNaN(valor)) return "—";
  if (!Number.isFinite(valor)) return valor > 0 ? "+∞" : "-∞";
  if (valor === 0) return "0";
  const abs = Math.abs(valor);
  if (abs < 1e-4 || abs >= 1e6) {
    return valor.toExponential(4);
  }
  return Number(valor.toFixed(decimales)).toString();
}

export default function TablaIteraciones({ datos }) {
  if (!datos) return null;

  const {
    nombre,
    convergio,
    estado,
    mensaje,
    advertencia,
    iteraciones_usadas: iteracionesUsadas,
    solucion,
    error_final: errorFinal,
    residuo_final: residuoFinal,
    historial,
  } = datos;

  const n = historial?.[0]?.x?.length ?? solucion?.length ?? 0;

  const badgeClase = convergio
    ? "border-emerald-200 bg-emerald-50 text-emerald-700"
    : estado === "divergencia"
      ? "border-inconsistente/30 bg-inconsistente/10 text-inconsistente"
      : "border-amber-200 bg-amber-50 text-amber-800";

  const badgeTexto = convergio
    ? `Convergió en ${iteracionesUsadas} iter.`
    : estado === "divergencia"
      ? "Divergencia detectada"
      : `Límite alcanzado (${iteracionesUsadas} iter.)`;

  return (
    <Panel
      className="math-panel"
      titulo={`Método de ${nombre}`}
      descripcion={
        nombre === "Jacobi"
          ? "Actualización simultánea: usa exclusivamente los valores x⁽ᵏ⁻¹⁾ de la iteración anterior."
          : "Actualización inmediata: utiliza los valores recién calculados dentro de la misma iteración k."
      }
      acciones={
        <span
          className={`rounded-full border px-3 py-1 text-xs font-semibold ${badgeClase}`}
        >
          {badgeTexto}
        </span>
      }
    >
      <div className="space-y-4">
        <p className="text-sm text-tinta">{mensaje}</p>

        {advertencia && (
          <div className="rounded-xl border border-inconsistente/30 bg-inconsistente/5 p-3 text-sm text-inconsistente">
            <strong>Advertencia:</strong> {advertencia}
          </div>
        )}

        {solucion && (
          <div className="grid gap-3 rounded-xl border border-[var(--borde)] bg-slate-50/80 p-3.5 sm:grid-cols-3">
            <div className="sm:col-span-2">
              <p className="text-xs font-semibold uppercase tracking-wider text-grafito">
                Solución aproximada x⁽{iteracionesUsadas}⁾
              </p>
              <p className="mt-1 font-mono text-sm font-semibold text-tinta">
                (
                {solucion
                  .map((v, i) => `x${subindice(i)} = ${formatearNumero(v, 7)}`)
                  .join(",  ")}
                )
              </p>
            </div>

            <div className="space-y-1 text-xs">
              <div>
                <span className="text-grafito">Error final ||Δx||∞: </span>
                <span className="font-mono font-semibold text-tinta">
                  {errorFinal !== null ? errorFinal.toExponential(4) : "—"}
                </span>
              </div>
              <div>
                <span className="text-grafito">Residuo ||Ax − b||∞: </span>
                <span className="font-mono font-semibold text-tinta">
                  {residuoFinal !== null ? residuoFinal.toExponential(4) : "—"}
                </span>
              </div>
            </div>
          </div>
        )}

        {historial && historial.length > 0 ? (
          <div className="max-h-96 overflow-auto rounded-xl border border-[var(--borde)]">
            <table className="min-w-full divide-y divide-[var(--borde)] text-left text-xs">
              <thead className="sticky top-0 bg-slate-100 text-grafito">
                <tr>
                  <th className="px-3 py-2.5 font-semibold">k</th>
                  {Array.from({ length: n }, (_, i) => (
                    <th key={i} className="px-3 py-2.5 font-semibold">
                      x{subindice(i)}
                    </th>
                  ))}
                  <th className="px-3 py-2.5 font-semibold">
                    Error ||x⁽ᵏ⁾ − x⁽ᵏ⁻¹⁾||∞
                  </th>
                  <th className="px-3 py-2.5 font-semibold">
                    Residuo ||Ax − b||∞
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 bg-white font-mono">
                {historial.map((fila) => (
                  <tr key={fila.k} className="hover:bg-slate-50/80">
                    <td className="px-3 py-2 font-semibold text-tinta">
                      {fila.k}
                    </td>
                    {fila.x.map((valor, idx) => (
                      <td key={idx} className="px-3 py-2 text-tinta">
                        {formatearNumero(valor, 6)}
                      </td>
                    ))}
                    <td className="px-3 py-2 text-slate-700">
                      {fila.error.toExponential(4)}
                    </td>
                    <td className="px-3 py-2 text-slate-700">
                      {fila.residuo.toExponential(4)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-xs text-grafito">
            No se registraron iteraciones válidas antes de detener el proceso.
          </p>
        )}
      </div>
    </Panel>
  );
}