// Tabla de comprobación: sustituye la solución en cada ecuación ORIGINAL y
// compara el resultado con el término independiente (comparación exacta).

import { textoFraccion } from "../lib/formato.js";

export default function PanelVerificacion({ verificacion }) {
  if (verificacion.length === 0) {
    return (
      <p className="text-sm text-grafito">
        No aplica: un sistema inconsistente no tiene solución que sustituir.
      </p>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm">
        <thead>
          <tr className="font-display text-grafito">
            <th className="py-2 pr-4">Ec.</th>
            <th className="py-2 pr-4">Sustitución</th>
            <th className="py-2 pr-4">Obtenido</th>
            <th className="py-2 pr-4">Esperado</th>
            <th className="py-2">¿Coincide?</th>
          </tr>
        </thead>
        <tbody className="font-mono nums-tabulares">
          {verificacion.map((comprobacion) => (
            <tr
              key={comprobacion.ecuacion}
              className="border-t border-[var(--borde)]"
            >
              <td className="py-2 pr-4">{comprobacion.ecuacion}</td>
              <td className="py-2 pr-4">{comprobacion.sustitucion}</td>
              <td className="py-2 pr-4">
                {textoFraccion(comprobacion.obtenido)}
              </td>
              <td className="py-2 pr-4">
                {textoFraccion(comprobacion.esperado)}
              </td>
              <td className="py-2">
                {comprobacion.coincide ? (
                  <span className="text-determinado">✓ sí</span>
                ) : (
                  <span className="text-inconsistente">✗ no</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
