import { useEffect, useState } from "react";
import {
  esUnidad,
  magnitudDe,
  nombreVariable,
  signoDe,
  textoDecimal,
  textoFraccion,
} from "../lib/formato.js";

function ValorVariable({ indice, valor }) {
  return (
    <div className="math-value-card">
      <span className="font-display text-lg font-semibold">
        {nombreVariable(indice)}
      </span>
      <span className="text-grafito">=</span>
      <span className="font-mono text-lg font-bold text-pivote nums-tabulares">
        {textoFraccion(valor)}
      </span>
      {!valor.es_entero && (
        <span className="font-mono text-xs text-grafito">
          ≈ {textoDecimal(valor)}
        </span>
      )}
    </div>
  );
}

function Termino({ coeficiente, texto, primero }) {
  const negativo = signoDe(coeficiente) === "−";
  const cuerpo =
    (esUnidad(coeficiente) ? "" : `${magnitudDe(coeficiente)}·`) + texto;

  if (primero) return <span>{negativo ? `−${cuerpo}` : cuerpo}</span>;
  return <span> {negativo ? "−" : "+"} {cuerpo}</span>;
}

function Vector({ valores }) {
  return (
    <span className="math-vector">
      ({valores.map((valor) => textoFraccion(valor)).join(", ")})
    </span>
  );
}

function FormaGeneral({ expresiones }) {
  return (
    <ul className="mt-3 space-y-2 font-mono text-sm sm:text-base nums-tabulares">
      {expresiones.map((expresion) => {
        const terminos = expresion.terminos_libres ?? [];
        const ocultarConstante =
          expresion.constante.fraccion === "0" && terminos.length > 0;

        return (
          <li key={expresion.variable} className="math-equation-line">
            <span className="font-semibold text-pivote">
              {nombreVariable(expresion.variable)}
            </span>{" "}
            ={" "}
            {!ocultarConstante && textoFraccion(expresion.constante)}
            {terminos.map((termino, indice) => (
              <Termino
                key={`${expresion.variable}-${termino.variable}`}
                coeficiente={termino.coeficiente}
                texto={nombreVariable(termino.variable)}
                primero={ocultarConstante && indice === 0}
              />
            ))}
            {expresion.es_libre && (
              <span className="ml-2 font-sans text-xs text-indeterminado">
                variable libre
              </span>
            )}
          </li>
        );
      })}
    </ul>
  );
}

function FormaParametrizada({ expresiones }) {
  return (
    <ul className="mt-3 space-y-2 font-mono text-sm sm:text-base nums-tabulares">
      {expresiones.map((expresion) => {
        const terminos = expresion.terminos ?? [];
        const ocultarConstante =
          expresion.constante.fraccion === "0" && terminos.length > 0;

        return (
          <li key={expresion.variable} className="math-equation-line">
            <span className="font-semibold text-pivote">
              {nombreVariable(expresion.variable)}
            </span>{" "}
            ={" "}
            {!ocultarConstante && textoFraccion(expresion.constante)}
            {terminos.map((termino, indice) => (
              <Termino
                key={`${expresion.variable}-${termino.parametro}`}
                coeficiente={termino.coeficiente}
                texto={termino.parametro}
                primero={ocultarConstante && indice === 0}
              />
            ))}
          </li>
        );
      })}
    </ul>
  );
}

export default function PanelSolucion({
  solucion,
  onEvaluarParametros,
  evaluando,
  errorParametros,
}) {
  const [valores, setValores] = useState([]);
  const claveParametros = (solucion.parametros ?? [])
    .map((parametro) => parametro.nombre)
    .join("|");

  useEffect(() => {
    setValores((solucion.parametros ?? []).map(() => ""));
  }, [claveParametros]);

  if (solucion.tipo === "determinado") {
    return (
      <div className="space-y-5">
        <div className="math-solution-banner math-solution-ok">
          <div className="math-solution-icon">✓</div>
          <div>
            <p className="font-display text-xl font-bold">Solución única</p>
            <p className="mt-1 text-sm text-grafito">
              Todas las variables son básicas; no se necesita ningún parámetro.
            </p>
          </div>
        </div>

        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {solucion.valores.map((entrada) => (
            <ValorVariable
              key={entrada.variable}
              indice={entrada.variable}
              valor={entrada.valor}
            />
          ))}
        </div>
      </div>
    );
  }

  if (solucion.tipo === "inconsistente") {
    const fila = solucion.fila_contradictoria;

    return (
      <div className="space-y-5">
        <div className="math-solution-banner math-solution-error">
          <div className="math-solution-icon">∅</div>
          <div>
            <p className="font-display text-xl font-bold">Sistema inconsistente</p>
            <p className="mt-1 text-sm text-grafito">
              No existe ningún vector que satisfaga simultáneamente todas las ecuaciones.
            </p>
          </div>
        </div>

        {fila && (
          <div className="math-form-card border-inconsistente/25">
            <p className="text-sm font-semibold text-inconsistente">
              Fila contradictoria en la RREF
            </p>
            <p className="mt-3 font-mono text-base nums-tabulares">
              [ {fila.coeficientes.map((valor) => textoFraccion(valor)).join("  ")} |{" "}
              {textoFraccion(fila.termino_independiente)} ]
            </p>
            <p className="mt-3 text-sm text-grafito">
              Equivale a <strong>0 = {textoFraccion(fila.termino_independiente)}</strong>,
              lo cual es imposible.
            </p>
          </div>
        )}
      </div>
    );
  }

  const general = solucion.forma_general ?? solucion.solucion_general ?? [];
  const parametrizada =
    solucion.forma_parametrizada ?? solucion.solucion_parametrizada ?? [];
  const vectorial = solucion.forma_vectorial ?? solucion.solucion_vectorial;
  const evaluacion = solucion.evaluacion_parametros;
  const parametros = solucion.parametros ?? [];
  const faltanValores =
    valores.length !== parametros.length ||
    valores.some((valor) => String(valor).trim() === "");

  return (
    <div className="space-y-6">
      <div className="math-solution-banner math-solution-infinite">
        <div className="math-solution-icon">∞</div>
        <div>
          <p className="font-display text-xl font-bold">Infinitas soluciones</p>
          <p className="mt-1 text-sm text-grafito">
            Las variables libres pueden tomar cualquier valor real. Elige un
            valor para el parámetro y el programa comprobará esa solución.
          </p>
        </div>
      </div>

      <div className="grid gap-3 md:grid-cols-2">
        <div className="math-info-card">
          <p className="text-xs font-semibold uppercase tracking-wide text-grafito">
            Variables básicas
          </p>
          <div className="mt-3 flex flex-wrap gap-2">
            {(solucion.variables_basicas ?? []).map((variable) => (
              <span key={variable} className="math-variable-pill">
                {nombreVariable(variable)}
              </span>
            ))}
          </div>
        </div>

        <div className="math-info-card math-info-free">
          <p className="text-xs font-semibold uppercase tracking-wide text-grafito">
            Variables libres
          </p>
          <div className="mt-3 flex flex-wrap gap-2">
            {(solucion.variables_libres ?? []).map((variable) => (
              <span key={variable} className="math-variable-pill">
                {nombreVariable(variable)}
              </span>
            ))}
          </div>
        </div>
      </div>

      <section className="math-form-card">
        <div className="flex items-center gap-3">
          <span className="math-section-number">1</span>
          <div>
            <h3 className="font-display text-lg font-bold">Solución general</h3>
            <p className="text-xs text-grafito">
              Variables básicas escritas en función de las variables libres.
            </p>
          </div>
        </div>
        <FormaGeneral expresiones={general} />
      </section>

      <section className="math-form-card">
        <div className="flex items-center gap-3">
          <span className="math-section-number">2</span>
          <div>
            <h3 className="font-display text-lg font-bold">Solución parametrizada</h3>
            <p className="text-xs text-grafito">
              Cada variable libre se reemplaza por t, o por t1, t2, ... si hay varias.
            </p>
          </div>
        </div>

        <div className="mt-3 flex flex-wrap gap-2">
          {parametros.map((parametro) => (
            <span key={parametro.nombre} className="math-param-chip">
              {nombreVariable(parametro.variable)} = {parametro.nombre}, {parametro.nombre} ∈ ℝ
            </span>
          ))}
        </div>

        <FormaParametrizada expresiones={parametrizada} />
      </section>

      {vectorial && (
        <section className="math-form-card">
          <div className="flex items-center gap-3">
            <span className="math-section-number">3</span>
            <div>
              <h3 className="font-display text-lg font-bold">Solución vectorial</h3>
              <p className="text-xs text-grafito">
                Vector particular más una dirección por cada parámetro libre.
              </p>
            </div>
          </div>

          <div className="math-vector-expression mt-4">
            <span className="font-mono font-bold">x =</span>
            <Vector valores={vectorial.vector_particular} />
            {vectorial.vectores_direccion.map((direccion) => (
              <span key={direccion.parametro} className="flex items-center gap-2">
                <span className="font-mono font-bold">+ {direccion.parametro}</span>
                <Vector valores={direccion.vector} />
              </span>
            ))}
          </div>
        </section>
      )}

      <section className="math-parameter-box">
        <div className="flex items-start gap-3">
          <span className="math-section-number math-section-number-light">4</span>
          <div>
            <h3 className="font-display text-lg font-bold text-white">
              Comprobación con un valor elegido por ti
            </h3>
            <p className="mt-1 text-sm text-white/80">
              Escribe cualquier número para cada parámetro. También puedes usar
              decimales o fracciones, por ejemplo 2, -3, 1/2.
            </p>
          </div>
        </div>

        <div className="mt-5 flex flex-wrap items-end gap-3">
          {parametros.map((parametro, indice) => (
            <label key={parametro.nombre} className="block">
              <span className="mb-1 block font-mono text-sm font-semibold text-white">
                {parametro.nombre} =
              </span>
              <input
                className="math-parameter-input"
                value={valores[indice] ?? ""}
                onChange={(evento) =>
                  setValores((previos) =>
                    previos.map((valor, posicion) =>
                      posicion === indice ? evento.target.value : valor
                    )
                  )
                }
                placeholder="Ej. 2"
                inputMode="text"
              />
            </label>
          ))}

          <button
            type="button"
            className="math-check-button"
            disabled={evaluando || faltanValores}
            onClick={() => onEvaluarParametros(valores)}
          >
            {evaluando ? "Comprobando…" : "Comprobar solución"}
          </button>
        </div>

        {faltanValores && !evaluacion && (
          <p className="mt-3 text-xs text-white/70">
            Ingresa un número en todos los parámetros para habilitar la comprobación.
          </p>
        )}

        {errorParametros && (
          <div className="mt-4 rounded-xl border border-white/20 bg-white/10 p-3 text-sm text-white">
            {errorParametros.message}
          </div>
        )}

        {evaluacion && (
          <div className="mt-5 rounded-2xl bg-white p-4 text-tinta shadow-lg">
            <p className="text-xs font-semibold uppercase tracking-wide text-grafito">
              Sustituyendo tus parámetros
            </p>
            <div className="mt-3 flex flex-wrap gap-2">
              {evaluacion.parametros.map((parametro) => (
                <span key={parametro.nombre} className="math-param-result">
                  {parametro.nombre} = {textoFraccion(parametro.valor)}
                </span>
              ))}
            </div>

            <p className="mt-4 text-sm font-semibold">Valores de las incógnitas:</p>
            <div className="mt-2 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
              {evaluacion.valores_variables.map((valor, indice) => (
                <ValorVariable key={indice} indice={indice} valor={valor} />
              ))}
            </div>

            <div className="mt-4 rounded-xl bg-determinado/10 px-3 py-2 text-sm font-semibold text-determinado">
              {evaluacion.verificacion.every((comprobacion) => comprobacion.coincide)
                ? "✓ La solución elegida satisface todas las ecuaciones originales."
                : "✗ La sustitución no coincide con alguna ecuación."}
            </div>
          </div>
        )}
      </section>
    </div>
  );
}
