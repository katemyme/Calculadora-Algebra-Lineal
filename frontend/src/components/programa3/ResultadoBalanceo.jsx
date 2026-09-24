// Resultado de la opción 12: balanceo de una ecuación química.
//
// NOTA DE CUMPLIMIENTO: este componente solo PINTA lo que devolvió el backend
// ("programas/Programa 3_GrupoX.py"). No realiza ninguna operación algebraica.

import { useState } from "react";
import Pestanas from "../ui/Pestanas.jsx";
import PanelProcedimiento from "../PanelProcedimiento.jsx";
import PanelClasificacion from "../PanelClasificacion.jsx";
import { VectorColumna } from "./comunes.jsx";

const PESTANAS = [
  { id: "resultado", etiqueta: "Resultado" },
  { id: "planteamiento", etiqueta: "Planteamiento" },
  { id: "procedimiento", etiqueta: "Procedimiento" },
  { id: "clasificacion", etiqueta: "Clasificación" },
  { id: "verificacion", etiqueta: "Verificación" },
];

// Mensaje cuando la reacción no queda balanceada.
const MENSAJE_ESTADO = {
  independientes:
    "Los vectores son linealmente independientes: la única solución es la trivial x = 0, así que la reacción no se puede balancear. Revise las fórmulas.",
  varias:
    "Hay más de una variable libre: la reacción admite varias combinaciones independientes y no tiene un balanceo único.",
  sin_enteros: "No se encontraron coeficientes enteros razonables.",
  no_valida:
    "Algún coeficiente es 0 o negativo: la reacción, tal como está escrita, no es químicamente válida (revise reactivos y productos).",
};

export default function ResultadoBalanceo({ resultado }) {
  const [activa, setActiva] = useState("resultado");

  return (
    <div
      className="math-panel overflow-hidden rounded-[var(--radio)] border border-[var(--borde)] bg-superficie"
      style={{ animation: "aparecer-paso 0.35s ease both" }}
    >
      <div className="math-results-header px-5 pt-4">
        <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
          <div>
            <p className="font-display text-lg font-bold">Balanceo de la ecuación química</p>
            <p className="text-xs text-grafito">
              Conservación de átomos → sistema homogéneo [A | 0] → Gauss-Jordan
            </p>
          </div>
          <span className="math-result-badge">x₁v₁ + … + xₖvₖ = 0</span>
        </div>
        <Pestanas pestanas={PESTANAS} activa={activa} onCambiar={setActiva} />
      </div>

      <div className="p-5 sm:p-6">
        {activa === "resultado" && <PanelBalanceo resultado={resultado} />}

        {activa === "planteamiento" && <PanelPlanteamiento resultado={resultado} />}

        {activa === "procedimiento" && (
          <PanelProcedimiento
            matrizInicial={resultado.matriz_inicial}
            pasos={resultado.pasos}
            matrizReducida={resultado.matriz_reducida}
            columnasPivote={resultado.columnas_pivote}
          />
        )}

        {activa === "clasificacion" && (
          <PanelClasificacion
            clasificacion={resultado.clasificacion}
            homogeneo={resultado.homogeneo}
            rangoA={resultado.rango_A}
            rangoAb={resultado.rango_Ab}
            n={resultado.k}
            columnasPivote={resultado.columnas_pivote.map((c) => c + 1)}
            variablesBasicas={resultado.solucion?.variables_basicas ?? []}
            variablesLibres={resultado.solucion?.variables_libres ?? []}
            letra="x"
            etiquetaN="compuestos k"
          />
        )}

        {activa === "verificacion" && <PanelVerificacionAtomos resultado={resultado} />}
      </div>
    </div>
  );
}

function Insignia({ correcto, children }) {
  return (
    <span
      className={`rounded-full px-3 py-1 text-xs font-semibold ${
        correcto ? "bg-determinado/10 text-determinado" : "bg-inconsistente/10 text-inconsistente"
      }`}
    >
      {children}
    </span>
  );
}

function PanelBalanceo({ resultado }) {
  const { estado, compuestos, coeficientes, rango, k, dependientes, solucion } = resultado;
  const balanceada = estado === "balanceada";

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap gap-2">
        <Insignia correcto={resultado.homogeneo}>
          {resultado.homogeneo ? "Sistema HOMOGÉNEO (b = 0)" : "Sistema NO HOMOGÉNEO"}
        </Insignia>
        <Insignia correcto={dependientes}>
          {dependientes
            ? `Vectores LINEALMENTE DEPENDIENTES (rango ${rango} < k = ${k})`
            : `Vectores LINEALMENTE INDEPENDIENTES (rango ${rango} = k = ${k})`}
        </Insignia>
      </div>

      <div className={`math-solution-banner ${balanceada ? "math-solution-ok" : "math-solution-error"}`}>
        <div
          className="math-solution-icon"
          style={{ color: `var(--${balanceada ? "determinado" : "inconsistente"})` }}
        >
          {balanceada ? "⇌" : "✗"}
        </div>
        <div className="min-w-0">
          <p
            className={`font-display text-sm font-semibold uppercase tracking-wide ${
              balanceada ? "text-determinado" : "text-inconsistente"
            }`}
          >
            {balanceada ? "Ecuación balanceada" : "No se pudo balancear"}
          </p>
          {balanceada ? (
            <p className="mt-1 break-words font-mono text-xl font-bold text-tinta sm:text-2xl">
              {resultado.ecuacion_balanceada}
            </p>
          ) : (
            <p className="mt-1 text-sm text-tinta">{MENSAJE_ESTADO[estado]}</p>
          )}
        </div>
      </div>

      {coeficientes && (
        <div className="space-y-2">
          <p className="text-xs font-semibold uppercase tracking-wide text-grafito">
            Coeficientes enteros mínimos
            {resultado.parametro_t != null && ` (tomando t = ${resultado.parametro_t})`}
          </p>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {compuestos.map((c) => (
              <div key={c.indice} className="math-value-card">
                <span className="font-display text-lg font-bold text-grafito">{c.variable}</span>
                <span className="text-grafito">=</span>
                <span className="font-mono text-xl font-bold text-determinado">
                  {coeficientes[c.indice]}
                </span>
                <span className="ml-auto font-mono text-sm text-grafito">{c.formula_bonita}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {solucion && dependientes && (
        <div className="math-form-card">
          <p className="text-xs font-semibold uppercase tracking-wide text-grafito">
            Solución general (forma paramétrica)
          </p>
          <ul className="mt-3 space-y-1.5 font-mono">
            {solucion.forma_parametrica.map((linea) => (
              <li key={linea.variable} className="math-equation-line flex items-center gap-2">
                <strong>{linea.nombre}</strong> = {linea.texto}
                {linea.es_libre && (
                  <span className="ml-auto rounded-full bg-indeterminado/10 px-2 py-0.5 text-xs text-indeterminado">
                    libre
                  </span>
                )}
              </li>
            ))}
          </ul>
          {balanceada && (
            <p className="mt-3 text-sm text-grafito">
              Se elige t = {resultado.parametro_t}, el menor valor que deja todos los
              coeficientes enteros.
            </p>
          )}
        </div>
      )}
    </div>
  );
}

function PanelPlanteamiento({ resultado }) {
  const { compuestos, ecuaciones, elementos } = resultado;

  return (
    <div className="space-y-5">
      <div className="math-form-card">
        <p className="text-xs font-semibold uppercase tracking-wide text-grafito">
          Variables
        </p>
        <ul className="mt-3 space-y-1.5">
          {compuestos.map((c) => (
            <li key={c.indice} className="math-equation-line flex flex-wrap items-center gap-2">
              <strong className="font-mono">{c.variable}</strong>
              <span>= coeficiente de</span>
              <strong className="font-mono">{c.formula_bonita}</strong>
              <span className="ml-auto rounded-full bg-pivote/10 px-2 py-0.5 text-xs text-pivote">
                {c.lado}
              </span>
            </li>
          ))}
        </ul>
      </div>

      <div className="math-form-card">
        <p className="text-xs font-semibold uppercase tracking-wide text-grafito">
          Sistema de ecuaciones (un elemento por ecuación, productos pasados a la izquierda)
        </p>
        <ul className="mt-3 space-y-1.5 font-mono">
          {ecuaciones.map((e) => (
            <li key={e.elemento} className="math-equation-line flex gap-3">
              <strong className="w-8 shrink-0">{e.elemento}</strong>
              <span>{e.texto}</span>
            </li>
          ))}
        </ul>
      </div>

      <div className="math-form-card">
        <p className="text-xs font-semibold uppercase tracking-wide text-grafito">
          Vectores de composición (componentes: {elementos.join(", ")})
        </p>
        <p className="mt-1 text-sm text-grafito">
          Los productos llevan signo negativo porque se pasaron al lado izquierdo.
        </p>
        <div className="mt-3 flex flex-wrap gap-5 overflow-x-auto">
          {compuestos.map((c) => (
            <div key={c.indice} className="flex flex-col items-center gap-1">
              <span className="font-display text-sm font-bold">
                v{c.variable.slice(1)}
              </span>
              <VectorColumna vector={c.vector} />
              <span className="font-mono text-xs text-grafito">{c.formula_bonita}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function PanelVerificacionAtomos({ resultado }) {
  if (resultado.verificacion.length === 0) {
    return (
      <div className="math-empty-verification">
        <div className="math-empty-icon">∅</div>
        <div>
          <p className="font-display text-lg font-bold">No hay balanceo que comprobar</p>
          <p className="mt-1 text-sm text-grafito">{MENSAJE_ESTADO[resultado.estado]}</p>
        </div>
      </div>
    );
  }

  const correcto = resultado.verificacion.every((v) => v.coincide);

  return (
    <div className="space-y-4">
      <p className="text-sm text-grafito">
        Se cuentan los átomos de cada elemento a cada lado con los coeficientes obtenidos.
      </p>
      <div className="overflow-x-auto">
        <table className="w-full max-w-md font-mono text-sm">
          <thead>
            <tr className="border-b border-[var(--borde)] text-left text-xs uppercase tracking-wide text-grafito">
              <th className="py-2 pr-4">Elemento</th>
              <th className="py-2 pr-4">Reactivos</th>
              <th className="py-2 pr-4">Productos</th>
              <th className="py-2" />
            </tr>
          </thead>
          <tbody>
            {resultado.verificacion.map((v) => (
              <tr key={v.elemento} className="border-b border-[var(--borde)]/60">
                <td className="py-2 pr-4 font-bold">{v.elemento}</td>
                <td className="py-2 pr-4">{v.reactivos}</td>
                <td className="py-2 pr-4">{v.productos}</td>
                <td className={`py-2 ${v.coincide ? "text-determinado" : "text-inconsistente"}`}>
                  {v.coincide ? "✓" : "✗"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div
        className={`rounded-xl border px-4 py-3 text-sm font-semibold ${
          correcto
            ? "border-determinado/25 bg-determinado/10 text-determinado"
            : "border-inconsistente/25 bg-inconsistente/10 text-inconsistente"
        }`}
      >
        {correcto
          ? "✓ Se conserva cada elemento: la ecuación está balanceada."
          : "✗ No coincide"}
      </div>
    </div>
  );
}
