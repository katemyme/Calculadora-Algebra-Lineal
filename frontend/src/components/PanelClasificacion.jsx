import { ESTILO_CLASIFICACION, nombreVariable } from "../lib/formato.js";

function Metrica({ etiqueta, valor }) {
  return (
    <div className="math-metric rounded-xl border border-[var(--borde)] px-3 py-4 text-center">
      <dt className="text-xs font-medium uppercase tracking-wide text-grafito">
        {etiqueta}
      </dt>
      <dd className="mt-1 font-mono text-2xl font-bold nums-tabulares">{valor}</dd>
    </div>
  );
}

function ListaVariables({ titulo, simbolo, valores, transformar }) {
  return (
    <div className="math-info-card">
      <div className="flex items-center gap-2">
        <span className="math-mini-symbol">{simbolo}</span>
        <p className="text-sm font-semibold">{titulo}</p>
      </div>
      <div className="mt-3 flex flex-wrap gap-2">
        {valores.length ? (
          valores.map((valor) => (
            <span key={valor} className="math-variable-pill">
              {transformar(valor)}
            </span>
          ))
        ) : (
          <span className="text-sm text-grafito">Ninguna</span>
        )}
      </div>
    </div>
  );
}

export default function PanelClasificacion({
  clasificacion,
  rangoA,
  rangoAb,
  n,
  columnasPivote,
  variablesBasicas,
  variablesLibres,
}) {
  const estilo =
    ESTILO_CLASIFICACION[clasificacion.tipo] ??
    ESTILO_CLASIFICACION.determinado;

  return (
    <div className="space-y-5">
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
        <p className="mt-2 text-sm leading-6 text-tinta/80">
          {clasificacion.explicacion}
        </p>
      </div>

      <dl className="grid grid-cols-1 gap-3 sm:grid-cols-3">
        <Metrica etiqueta="rango(A)" valor={rangoA} />
        <Metrica etiqueta="rango(A|b)" valor={rangoAb} />
        <Metrica etiqueta="incógnitas n" valor={n} />
      </dl>

      <div className="grid gap-3 lg:grid-cols-3">
        <ListaVariables
          titulo="Columnas pivote"
          simbolo="P"
          valores={columnasPivote}
          transformar={(columna) => `Columna ${columna}`}
        />
        <ListaVariables
          titulo="Variables básicas"
          simbolo="B"
          valores={variablesBasicas}
          transformar={nombreVariable}
        />
        <ListaVariables
          titulo="Variables libres"
          simbolo="L"
          valores={variablesLibres}
          transformar={nombreVariable}
        />
      </div>

      {clasificacion.grados_de_libertad > 0 && (
        <div className="math-note">
          <span className="font-mono">n − rango(A) = </span>
          <strong>{clasificacion.grados_de_libertad}</strong> grado(s) de libertad.
        </div>
      )}
    </div>
  );
}
