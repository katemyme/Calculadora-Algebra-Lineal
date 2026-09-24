// Resultado de la opción 10: ¿son v₁, …, vₖ linealmente independientes?
//
// NOTA DE CUMPLIMIENTO: este componente solo PINTA lo que devolvió el backend
// ("programas/Programa 3_GrupoX.py"). No realiza ninguna operación algebraica.

import { useState } from "react";
import { subindice } from "../../lib/formato.js";
import Pestanas from "../ui/Pestanas.jsx";
import PanelProcedimiento from "../PanelProcedimiento.jsx";
import PanelClasificacion from "../PanelClasificacion.jsx";
import { Operador, VectorColumna, textoVector } from "./comunes.jsx";

const PESTANAS = [
  { id: "resultado", etiqueta: "Resultado" },
  { id: "relaciones", etiqueta: "Relaciones" },
  { id: "procedimiento", etiqueta: "Procedimiento" },
  { id: "clasificacion", etiqueta: "Clasificación" },
  { id: "verificacion", etiqueta: "Verificación" },
];

export default function ResultadoIndependencia({ resultado }) {
  const [activa, setActiva] = useState("resultado");

  return (
    <div
      className="math-panel overflow-hidden rounded-[var(--radio)] border border-[var(--borde)] bg-superficie"
      style={{ animation: "aparecer-paso 0.35s ease both" }}
    >
      <div className="math-results-header px-5 pt-4">
        <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
          <div>
            <p className="font-display text-lg font-bold">
              ¿Son linealmente independientes?
            </p>
            <p className="text-xs text-grafito">
              Se resuelve el sistema homogéneo [v₁ … vₖ | 0] por Gauss-Jordan
            </p>
          </div>
          <span className="math-result-badge">c₁v₁ + … + cₖvₖ = 0</span>
        </div>
        <Pestanas pestanas={PESTANAS} activa={activa} onCambiar={setActiva} />
      </div>

      <div className="p-5 sm:p-6">
        {activa === "resultado" && <PanelVeredicto resultado={resultado} />}

        {activa === "relaciones" && <PanelRelaciones resultado={resultado} />}

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
            letra="c"
            etiquetaN="vectores k"
          />
        )}

        {activa === "verificacion" && <PanelVerificacion resultado={resultado} />}
      </div>
    </div>
  );
}

/** Tarjeta con una métrica grande (rango, k, dimensión del generado). */
function Metrica({ etiqueta, valor, resalte = false }) {
  return (
    <div className="math-value-card flex-col items-start gap-0.5">
      <span className="text-xs font-semibold uppercase tracking-wide text-grafito">
        {etiqueta}
      </span>
      <span
        className={`font-mono text-2xl font-bold nums-tabulares ${
          resalte ? "text-pivote" : "text-tinta"
        }`}
      >
        {valor}
      </span>
    </div>
  );
}

function PanelVeredicto({ resultado }) {
  const { independientes, rango, k, n, relacion } = resultado;

  return (
    <div className="space-y-5">
      <div
        className={`math-solution-banner ${
          independientes ? "math-solution-ok" : "math-solution-error"
        }`}
      >
        <div
          className="math-solution-icon"
          style={{ color: `var(--${independientes ? "determinado" : "inconsistente"})` }}
        >
          {independientes ? "⊥" : "∥"}
        </div>
        <div>
          <p
            className={`font-display text-xl font-bold ${
              independientes ? "text-determinado" : "text-inconsistente"
            }`}
          >
            {independientes
              ? "Los vectores son LINEALMENTE INDEPENDIENTES"
              : "Los vectores son LINEALMENTE DEPENDIENTES"}
          </p>
          <p className="mt-1 text-sm text-tinta">
            {independientes ? (
              <>
                rango = {rango} = k = {k}: no hay variables libres, así que la única
                solución de c₁·v₁ + … + cₖ·vₖ = 0 es la trivial c₁ = … = cₖ = 0.
              </>
            ) : (
              <>
                rango = {rango} &lt; k = {k}: quedan {k - rango} variable(s) libre(s), así
                que c₁·v₁ + … + cₖ·vₖ = 0 tiene soluciones distintas de la trivial.
              </>
            )}
          </p>
        </div>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Metrica etiqueta="Vectores k" valor={k} />
        <Metrica etiqueta="Dimensión n" valor={n} />
        <Metrica etiqueta="Rango" valor={rango} resalte />
        <Metrica etiqueta="dim del generado" valor={resultado.dimension_generado} />
      </div>

      {resultado.mas_vectores_que_dimensiones && (
        <p className="math-note">
          Son <strong>k = {k}</strong> vectores en ℝ<sup>{n}</sup> con k &gt; n: el rango
          nunca puede pasar de {n}, así que la dependencia estaba garantizada de antemano.
        </p>
      )}

      {independientes ? (
        <div className="math-form-card">
          <p className="text-xs font-semibold uppercase tracking-wide text-grafito">
            Consecuencias
          </p>
          <ul className="mt-2 space-y-1 text-sm text-tinta">
            <li>· Ningún vᵢ es combinación lineal de los demás.</li>
            <li>
              · Forman una base del subespacio que generan (dimensión {rango}).
            </li>
          </ul>
        </div>
      ) : (
        <>
          <div className="math-form-card">
            <p className="text-xs font-semibold uppercase tracking-wide text-grafito">
              Relación de dependencia (c{subindice(relacion.indice_libre + 1)} = 1, resto
              de variables libres = 0)
            </p>
            <p className="mt-2 font-mono text-xl font-bold text-pivote">
              {relacion.expresion}
            </p>
            <p className="mt-3 font-mono text-sm text-grafito">
              {relacion.pesos
                .map((peso, j) => `c${subindice(j + 1)} = ${peso.fraccion}`)
                .join(", ")}
            </p>
          </div>

          <div className="math-form-card">
            <p className="text-xs font-semibold uppercase tracking-wide text-grafito">
              Despejando el vector redundante
            </p>
            <p className="mt-2 font-mono text-xl font-bold text-inconsistente">
              {relacion.texto_despeje}
            </p>
          </div>

          <div className="math-form-card">
            <p className="text-xs font-semibold uppercase tracking-wide text-grafito">
              Subconjunto linealmente independiente (columnas pivote)
            </p>
            <div className="mt-3 flex flex-wrap items-center gap-2">
              {resultado.vectores_pivote.map((c) => (
                <span key={c} className="math-variable-pill">
                  v{subindice(c + 1)}
                </span>
              ))}
              <span className="ml-2 text-sm text-grafito">
                → generan un subespacio de dimensión {resultado.dimension_generado}.
              </span>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

function PanelRelaciones({ resultado }) {
  const { solucion, independientes } = resultado;

  if (independientes) {
    return (
      <div className="math-empty-verification">
        <div className="math-empty-icon">◇</div>
        <div>
          <p className="font-display text-lg font-bold">
            Solo existe la relación trivial
          </p>
          <p className="mt-1 text-sm text-grafito">
            El sistema homogéneo tiene solución única c₁ = c₂ = … = cₖ = 0, que no es una
            relación de dependencia.
          </p>
        </div>
      </div>
    );
  }

  const { forma_parametrica: forma, forma_vectorial: vectorial } = solucion;

  return (
    <div className="space-y-4">
      <p className="text-sm text-grafito">
        Toda solución del sistema homogéneo es una relación de dependencia. Estos son
        todos los coeficientes (c₁, …, cₖ) que anulan la combinación.
      </p>
      <div className="grid gap-4 lg:grid-cols-2">
        <div className="math-form-card">
          <p className="text-xs font-semibold uppercase tracking-wide text-grafito">
            Solución general (forma paramétrica)
          </p>
          <ul className="mt-3 space-y-1.5 font-mono">
            {forma.map((linea) => (
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
        </div>

        <div className="math-form-card">
          <p className="text-xs font-semibold uppercase tracking-wide text-grafito">
            Forma vectorial
          </p>
          <div className="math-vector-expression mt-3">
            <span className="font-display text-lg font-bold">c =</span>
            <VectorColumna vector={vectorial.particular} />
            {vectorial.direcciones.map((d) => (
              <span key={d.parametro} className="flex items-center gap-2">
                <Operador>+</Operador>
                <span className="font-mono text-lg font-bold text-pivote">
                  {d.parametro}
                </span>
                <VectorColumna vector={d.vector} />
              </span>
            ))}
          </div>
          <p className="mt-3 font-mono text-sm text-grafito">
            c = {textoVector(vectorial.particular)}
            {vectorial.direcciones.map((d) => ` + ${d.parametro}·${textoVector(d.vector)}`)}
          </p>
        </div>
      </div>
    </div>
  );
}

function PanelVerificacion({ resultado }) {
  const verificacion = resultado.verificaciones[0];

  if (!verificacion) {
    return (
      <div className="math-empty-verification">
        <div className="math-empty-icon">◇</div>
        <div>
          <p className="font-display text-lg font-bold">No hay relación que comprobar</p>
          <p className="mt-1 text-sm text-grafito">
            Al ser independientes, la única combinación que da 0 es la que tiene todos los
            coeficientes nulos.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <p className="text-sm text-grafito">
        Se recalcula Σ cᵢ·vᵢ con las operaciones de ℝⁿ y se comprueba que da el vector
        cero.
      </p>
      <div className="p3-lienzo">
        {verificacion.terminos.map((t, j) => (
          <span key={j} className="flex items-center gap-2">
            {j > 0 && <Operador>+</Operador>}
            <span className="font-mono text-lg font-bold text-pivote">
              {t.peso.fraccion}
            </span>
            <VectorColumna vector={t.vector} />
          </span>
        ))}
        <Operador>=</Operador>
        <VectorColumna vector={verificacion.recalculado} />
        <Operador>{verificacion.coincide ? "=" : "≠"}</Operador>
        <span className="flex items-center gap-2">
          <span className="font-display text-lg font-bold">0</span>
          <VectorColumna vector={verificacion.esperado} />
        </span>
      </div>
      <p className="font-mono text-sm">
        Σ cᵢ·vᵢ = {textoVector(verificacion.recalculado)} · 0 ={" "}
        {textoVector(verificacion.esperado)}
      </p>
      <div
        className={`rounded-xl border px-4 py-3 text-sm font-semibold ${
          verificacion.coincide
            ? "border-determinado/25 bg-determinado/10 text-determinado"
            : "border-inconsistente/25 bg-inconsistente/10 text-inconsistente"
        }`}
      >
        {verificacion.coincide
          ? "✓ Coinciden: la relación de dependencia es correcta."
          : "✗ No coinciden."}
      </div>
    </div>
  );
}
