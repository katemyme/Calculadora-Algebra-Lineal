import { textoFraccion } from "../lib/formato.js";

export default function PanelVerificacion({
  verificacion,
  requiereParametros = false,
}) {
  if (verificacion.length === 0) {
    if (requiereParametros) {
      return (
        <div className="math-empty-verification">
          <div className="math-empty-icon">t</div>
          <div>
            <p className="font-display text-lg font-bold">
              Falta elegir el parámetro
            </p>
            <p className="mt-1 text-sm text-grafito">
              Ve a la pestaña <strong>Solución</strong>, ingresa un número para t
              (o para t1, t2, ...), y presiona <strong>Comprobar solución</strong>.
              Después aparecerá aquí la sustitución en cada ecuación original.
            </p>
          </div>
        </div>
      );
    }

    return (
      <div className="math-empty-verification">
        <div className="math-empty-icon">∅</div>
        <div>
          <p className="font-display text-lg font-bold">No hay solución que comprobar</p>
          <p className="mt-1 text-sm text-grafito">
            Un sistema inconsistente no posee valores que puedan sustituirse.
          </p>
        </div>
      </div>
    );
  }

  const todasCoinciden = verificacion.every(
    (comprobacion) => comprobacion.coincide
  );

  return (
    <div className="space-y-4">
      <div
        className={`rounded-xl border px-4 py-3 text-sm font-semibold ${
          todasCoinciden
            ? "border-determinado/25 bg-determinado/10 text-determinado"
            : "border-inconsistente/25 bg-inconsistente/10 text-inconsistente"
        }`}
      >
        {todasCoinciden
          ? "✓ Comprobación correcta: todas las ecuaciones coinciden."
          : "✗ Alguna ecuación no coincide."}
      </div>

      <div className="overflow-x-auto rounded-xl border border-[var(--borde)]">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-50">
            <tr className="font-display text-grafito">
              <th className="px-4 py-3">Ec.</th>
              <th className="px-4 py-3">Sustitución</th>
              <th className="px-4 py-3">Obtenido</th>
              <th className="px-4 py-3">Esperado</th>
              <th className="px-4 py-3">¿Coincide?</th>
            </tr>
          </thead>
          <tbody className="font-mono nums-tabulares">
            {verificacion.map((comprobacion) => (
              <tr
                key={comprobacion.ecuacion}
                className="border-t border-[var(--borde)] bg-white transition-colors hover:bg-slate-50/70"
              >
                <td className="px-4 py-3 font-bold">{comprobacion.ecuacion}</td>
                <td className="px-4 py-3">{comprobacion.sustitucion}</td>
                <td className="px-4 py-3">
                  {textoFraccion(comprobacion.obtenido)}
                </td>
                <td className="px-4 py-3">
                  {textoFraccion(comprobacion.esperado)}
                </td>
                <td className="px-4 py-3">
                  {comprobacion.coincide ? (
                    <span className="font-semibold text-determinado">✓ sí</span>
                  ) : (
                    <span className="font-semibold text-inconsistente">✗ no</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
