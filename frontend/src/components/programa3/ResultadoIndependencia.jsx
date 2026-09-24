// Resultado de la opción 10: ¿son v₁, …, vₖ linealmente independientes?
//
// La pestaña "Solución" concentra el diagnóstico completo: independencia,
// homogeneidad, solución trivial, clasificación, forma paramétrica/vectorial,
// evaluación de parámetros y verificación. El álgebra sigue haciéndose en el
// backend; este componente únicamente presenta los datos y solicita evaluar t.

import { useEffect, useState } from "react";
import { subindice } from "../../lib/formato.js";
import Pestanas from "../ui/Pestanas.jsx";
import Boton from "../ui/Boton.jsx";
import PanelProcedimiento from "../PanelProcedimiento.jsx";
import PanelClasificacion from "../PanelClasificacion.jsx";
import { Operador, VectorColumna, textoVector } from "./comunes.jsx";

const PESTANAS = [
  { id: "solucion", etiqueta: "Solución" },
  { id: "procedimiento", etiqueta: "Procedimiento" },
];

export default function ResultadoIndependencia({ resultado, onEvaluar }) {
  const [activa, setActiva] = useState("solucion");

  return (
    <div
      className="math-panel overflow-hidden rounded-[var(--radio)] border border-[var(--borde)] bg-superficie"
      style={{ animation: "aparecer-paso 0.35s ease both" }}
    >
      <div className="math-results-header px-5 pt-4">
        <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
          <div>
            <p className="font-display text-lg font-bold">
              Solución de independencia lineal
            </p>
            <p className="text-xs text-grafito">
              Se resuelve el sistema homogéneo [v₁ … vₖ | 0] por Gauss-Jordan
            </p>
          </div>
          <span className="math-result-badge">x₁v₁ + … + xₖvₖ = 0</span>
        </div>
        <Pestanas pestanas={PESTANAS} activa={activa} onCambiar={setActiva} />
      </div>

      <div className="p-5 sm:p-6">
        {activa === "solucion" && (
          <PanelSolucionCompleta resultado={resultado} onEvaluar={onEvaluar} />
        )}

        {activa === "procedimiento" && (
          <PanelProcedimiento
            matrizInicial={resultado.matriz_inicial}
            pasos={resultado.pasos}
            matrizReducida={resultado.matriz_reducida}
            columnasPivote={resultado.columnas_pivote}
          />
        )}
      </div>
    </div>
  );
}

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

function Estado({ etiqueta, valor, detalle = null }) {
  return (
    <div className="math-info-card">
      <p className="text-xs font-semibold uppercase tracking-wide text-grafito">
        {etiqueta}
      </p>
      <p className="mt-1 font-display text-lg font-bold text-tinta">{valor}</p>
      {detalle && <p className="mt-1 text-xs leading-5 text-grafito">{detalle}</p>}
    </div>
  );
}

function PanelSolucionCompleta({ resultado, onEvaluar }) {
  const { independientes, rango, k, n, relacion, solucion } = resultado;

  return (
    <div className="space-y-6">
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
                rango = {rango} = k = {k}: no hay variables libres. La única solución de
                x₁·v₁ + … + xₖ·vₖ = 0 es la trivial.
              </>
            ) : (
              <>
                rango = {rango} &lt; k = {k}: quedan {k - rango} variable(s) libre(s), por
                lo que existen soluciones no triviales.
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

      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
        <Estado
          etiqueta="Tipo de sistema"
          valor={resultado.es_homogeneo ? "Homogéneo" : "No homogéneo"}
          detalle="El lado derecho es el vector 0."
        />
        <Estado
          etiqueta="Solución trivial"
          valor={resultado.tiene_solucion_trivial ? "Sí existe" : "No existe"}
          detalle="x₁ = x₂ = … = xₖ = 0."
        />
        <Estado
          etiqueta="Soluciones no triviales"
          valor={resultado.tiene_soluciones_no_triviales ? "Sí existen" : "No existen"}
          detalle={
            resultado.tiene_soluciones_no_triviales
              ? "Aparecen porque hay al menos una variable libre."
              : "La solución trivial es la única."
          }
        />
        <Estado
          etiqueta="Clasificación"
          valor={resultado.clasificacion.titulo}
          detalle={resultado.clasificacion.explicacion}
        />
      </div>

      {resultado.mas_vectores_que_dimensiones && (
        <p className="math-note">
          Son <strong>k = {k}</strong> vectores en ℝ<sup>{n}</sup> con k &gt; n: el rango
          nunca puede pasar de {n}, así que la dependencia estaba garantizada de antemano.
        </p>
      )}

      <div>
        <p className="mb-3 font-display text-lg font-bold text-tinta">
          Clasificación algebraica
        </p>
        <PanelClasificacion
          clasificacion={resultado.clasificacion}
          rangoA={resultado.rango_A}
          rangoAb={resultado.rango_Ab}
          n={resultado.k}
          columnasPivote={resultado.columnas_pivote.map((c) => c + 1)}
          variablesBasicas={solucion?.variables_basicas ?? []}
          variablesLibres={solucion?.variables_libres ?? []}
          letra="x"
          etiquetaN="incógnitas k"
        />
      </div>

      <PanelSolucionGeneral solucion={solucion} />

      {!independientes && (
        <EvaluadorParametros solucion={solucion} onEvaluar={onEvaluar} />
      )}

      {!independientes && relacion && (
        <div className="grid gap-4 lg:grid-cols-2">
          <div className="math-form-card">
            <p className="text-xs font-semibold uppercase tracking-wide text-grafito">
              Una relación de dependencia
            </p>
            <p className="mt-2 font-mono text-xl font-bold text-pivote">
              {relacion.expresion}
            </p>
            <p className="mt-3 font-mono text-sm text-grafito">
              {relacion.pesos
                .map((peso, j) => `x${subindice(j + 1)} = ${peso.fraccion}`)
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
        </div>
      )}

      {!independientes && (
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
      )}

      <PanelVerificacion resultado={resultado} />
    </div>
  );
}

function PanelSolucionGeneral({ solucion }) {
  if (!solucion) return null;
  const { forma_parametrica: forma, forma_vectorial: vectorial } = solucion;

  return (
    <div className="space-y-3">
      <p className="font-display text-lg font-bold text-tinta">
        Solución general parametrizada
      </p>
      <div className="grid gap-4 lg:grid-cols-2">
        <div className="math-form-card">
          <p className="text-xs font-semibold uppercase tracking-wide text-grafito">
            Forma paramétrica — usando x y fracciones
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
            <span className="font-display text-lg font-bold">x =</span>
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
            x = {textoVector(vectorial.particular)}
            {vectorial.direcciones.map((d) => ` + ${d.parametro}·${textoVector(d.vector)}`)}
          </p>
        </div>
      </div>
    </div>
  );
}

function EvaluadorParametros({ solucion, onEvaluar }) {
  const parametros = solucion?.parametros ?? [];
  const [valores, setValores] = useState(() => parametros.map(() => ""));
  const [evaluacion, setEvaluacion] = useState(null);
  const [error, setError] = useState("");
  const [cargando, setCargando] = useState(false);

  useEffect(() => {
    setValores(parametros.map(() => ""));
    setEvaluacion(null);
    setError("");
  }, [parametros.join("|")]);

  if (!parametros.length) return null;

  async function evaluar() {
    setCargando(true);
    setError("");
    setEvaluacion(null);
    try {
      const datos = await onEvaluar(valores);
      setEvaluacion(datos);
    } catch (excepcion) {
      setError(excepcion?.message ?? "No se pudo evaluar el parámetro.");
    } finally {
      setCargando(false);
    }
  }

  return (
    <div className="math-form-card">
      <p className="font-display text-lg font-bold text-tinta">
        Evaluar la solución con un valor elegido
      </p>
      <p className="mt-1 text-sm text-grafito">
        Escribe cualquier número o fracción para {parametros.length === 1 ? parametros[0] : "los parámetros"}.
        El programa sustituye esos valores en la solución general y devuelve el vector x.
      </p>

      <div className="mt-4 flex flex-wrap items-end gap-3">
        {parametros.map((parametro, i) => (
          <label key={parametro} className="flex flex-col gap-1">
            <span className="text-xs font-semibold text-grafito">{parametro}</span>
            <input
              type="text"
              inputMode="text"
              placeholder={parametros.length === 1 ? "Ej. 3" : "Ej. 1/2"}
              value={valores[i]}
              onChange={(evento) => {
                const copia = [...valores];
                copia[i] = evento.target.value;
                setValores(copia);
                setEvaluacion(null);
                setError("");
              }}
              className="h-10 w-28 rounded-lg border border-[var(--borde)] bg-white px-3 text-center font-mono focus:border-pivote"
            />
          </label>
        ))}
        <Boton onClick={evaluar} disabled={cargando}>
          {cargando ? "Evaluando…" : "Obtener conjunto solución"}
        </Boton>
      </div>

      {error && (
        <p className="mt-3 rounded-lg border border-inconsistente/25 bg-inconsistente/10 px-3 py-2 text-sm text-inconsistente">
          {error}
        </p>
      )}

      {evaluacion && (
        <div className="mt-4 rounded-xl border border-pivote/25 bg-pivote/5 p-4">
          <p className="text-xs font-semibold uppercase tracking-wide text-grafito">
            Sustitución elegida
          </p>
          <p className="mt-1 font-mono text-sm text-tinta">
            {evaluacion.parametros
              .map((p) => `${p.nombre} = ${p.valor.fraccion}`)
              .join(", ")}
          </p>
          <p className="mt-3 font-mono text-xl font-bold text-pivote">
            x = {evaluacion.texto_vector}
          </p>
          <p className="mt-2 font-mono text-base text-tinta">
            Conjunto solución evaluado: S = {evaluacion.conjunto_solucion}
          </p>
          <p className="mt-2 text-sm text-grafito">
            {evaluacion.es_trivial
              ? "El valor elegido produce la solución trivial."
              : "El valor elegido produce una solución no trivial."}
            {evaluacion.verificacion.coincide
              ? " La sustitución verifica x₁v₁ + … + xₖvₖ = 0."
              : " La verificación no coincide."}
          </p>
        </div>
      )}
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
          <p className="font-display text-lg font-bold">Verificación</p>
          <p className="mt-1 text-sm text-grafito">
            Al ser independientes, la única combinación que da 0 es x = 0.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <p className="font-display text-lg font-bold text-tinta">Verificación</p>
      <p className="text-sm text-grafito">
        Se recalcula Σ xᵢ·vᵢ y se comprueba que el resultado sea el vector cero.
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
