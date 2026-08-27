// Veredicto del sistema y la comparación de rangos que lo justifica.

import { ESTILO_CLASIFICACION } from "../lib/formato.js";

function Metrica({ etiqueta, valor }) {
  return (
    <div className="rounded-lg border border-[var(--borde)] py-3">
      <dt className="text-xs text-grafito">{etiqueta}</dt>
      <dd className="mt-1 font-mono text-2xl nums-tabulares">{valor}</dd>
    </div>
  );
}

export default function PanelClasificacion({
  clasificacion,
  rangoA,
  rangoAb,
  n,
}) {
  const estilo =
    ESTILO_CLASIFICACION[clasificacion.tipo] ??
    ESTILO_CLASIFICACION.determinado;

  return (
    <div>
      <div
        className={`rounded-[var(--radio)] border-l-4 p-5 ${estilo.clasesTarjeta}`}
      >
        <p
          className={`font-mono text-xs uppercase tracking-[0.2em] ${estilo.clasesTexto}`}
        >
          {estilo.icono} {estilo.etiqueta}
        </p>
        <p className="mt-1 font-display text-2xl font-bold">
          {clasificacion.titulo}
        </p>
        <p className="mt-2 text-sm text-tinta/80">{clasificacion.explicacion}</p>
      </div>

      <dl className="mt-4 grid grid-cols-3 gap-3 text-center">
        <Metrica etiqueta="rango(A)" valor={rangoA} />
        <Metrica etiqueta="rango(A|b)" valor={rangoAb} />
        <Metrica etiqueta="n (incógnitas)" valor={n} />
      </dl>

      {clasificacion.grados_de_libertad > 0 && (
        <p className="mt-3 text-sm text-grafito">
          Grados de libertad: {clasificacion.grados_de_libertad} variable(s)
          libre(s) (n − rango(A)).
        </p>
      )}
    </div>
  );
}
