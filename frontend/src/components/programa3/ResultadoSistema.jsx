// Resultado de un sistema resuelto por Gauss-Jordan en el Programa 3.
// Se usa para la combinación lineal (incógnitas c₁…cₖ) y para A·x = b.

import { useState } from "react";
import { ESTILO_CLASIFICACION, subindice } from "../../lib/formato.js";
import Pestanas from "../ui/Pestanas.jsx";
import PanelProcedimiento from "../PanelProcedimiento.jsx";
import PanelClasificacion from "../PanelClasificacion.jsx";
import MatrizEstatica from "../MatrizEstatica.jsx";
import { Operador, VectorColumna, textoVector } from "./comunes.jsx";

const PESTANAS = [
  { id: "resultado", etiqueta: "Resultado" },
  { id: "procedimiento", etiqueta: "Procedimiento" },
  { id: "clasificacion", etiqueta: "Clasificación" },
  { id: "verificacion", etiqueta: "Verificación" },
];

export default function ResultadoSistema({ resultado, modo }) {
  const [activa, setActiva] = useState("resultado");
  const esCombinacion = modo === "combinacion";
  const letra = esCombinacion ? "c" : "x";
  const incognitas = resultado.matriz_inicial[0].length - 1;

  return (
    <div
      className="math-panel overflow-hidden rounded-[var(--radio)] border border-[var(--borde)] bg-superficie"
      style={{ animation: "aparecer-paso 0.35s ease both" }}
    >
      <div className="math-results-header px-5 pt-4">
        <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
          <div>
            <p className="font-display text-lg font-bold">
              {esCombinacion ? "¿Es b combinación lineal?" : "Solución de A·x = b"}
            </p>
            <p className="text-xs text-grafito">
              {esCombinacion
                ? "Se resuelve [v₁ … vₖ | b] con los vectores como columnas"
                : "Se forma [A | b] y se reduce por Gauss-Jordan"}
            </p>
          </div>
          <span className="math-result-badge">
            {esCombinacion ? "c₁v₁ + … + cₖvₖ = b" : "Ax = b"}
          </span>
        </div>
        <Pestanas pestanas={PESTANAS} activa={activa} onCambiar={setActiva} />
      </div>

      <div className="p-5 sm:p-6">
        {activa === "resultado" && (
          <PanelRespuesta resultado={resultado} letra={letra} esCombinacion={esCombinacion} />
        )}

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
            n={incognitas}
            columnasPivote={resultado.columnas_pivote.map((c) => c + 1)}
            variablesBasicas={resultado.solucion?.variables_basicas ?? []}
            variablesLibres={resultado.solucion?.variables_libres ?? []}
            letra={letra}
            etiquetaN={esCombinacion ? "vectores k" : "incógnitas n"}
          />
        )}

        {activa === "verificacion" &&
          (esCombinacion ? (
            <VerificacionCombinacion resultado={resultado} />
          ) : (
            <VerificacionEcuacion resultado={resultado} />
          ))}
      </div>
    </div>
  );
}

function PanelRespuesta({ resultado, letra, esCombinacion }) {
  const { clasificacion, solucion } = resultado;
  const estilo = ESTILO_CLASIFICACION[clasificacion.tipo];

  if (clasificacion.tipo === "inconsistente") {
    const fila = resultado.fila_contradictoria;
    return (
      <div className="space-y-4">
        <div className="math-solution-banner math-solution-error">
          <div className="math-solution-icon" style={{ color: "var(--inconsistente)" }}>∅</div>
          <div>
            <p className="font-display text-xl font-bold text-inconsistente">
              {esCombinacion
                ? "b NO es combinación lineal de los vectores"
                : "El sistema no tiene solución"}
            </p>
            <p className="mt-1 text-sm text-tinta">{clasificacion.explicacion}</p>
          </div>
        </div>
        {fila && (
          <p className="math-note font-mono">
            La fila {fila.indice + 1} de la RREF dice{" "}
            <strong>0 = {fila.valor.fraccion}</strong>, una ecuación imposible.
          </p>
        )}
      </div>
    );
  }

  const esUnica = clasificacion.tipo === "determinado";

  return (
    <div className="space-y-5">
      <div
        className={`math-solution-banner ${esUnica ? "math-solution-ok" : "math-solution-infinite"}`}
      >
        <div className="math-solution-icon" style={{ color: `var(--${estilo.color})` }}>
          {estilo.icono}
        </div>
        <div>
          <p className={`font-display text-xl font-bold ${estilo.clasesTexto}`}>
            {esCombinacion
              ? esUnica
                ? "b SÍ es combinación lineal (pesos únicos)"
                : "b SÍ es combinación lineal (infinitas formas)"
              : esUnica
                ? "Solución única"
                : "Infinitas soluciones"}
          </p>
          <p className="mt-1 text-sm text-tinta">{clasificacion.explicacion}</p>
        </div>
      </div>

      {esUnica ? (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {solucion.valores.map((valor, j) => (
            <div key={j} className="math-value-card">
              <span className="font-display text-lg font-bold text-grafito">
                {letra}
                {subindice(j + 1)}
              </span>
              <span className="text-grafito">=</span>
              <span className="font-mono text-xl font-bold text-determinado">
                {valor.fraccion}
              </span>
            </div>
          ))}
        </div>
      ) : (
        <FormaParametrica solucion={solucion} letra={letra} />
      )}

      {esCombinacion && resultado.expresion && (
        <div className="math-form-card">
          <p className="text-xs font-semibold uppercase tracking-wide text-grafito">
            {esUnica ? "Combinación lineal" : "Combinación particular (variables libres = 0)"}
          </p>
          <p className="mt-2 font-mono text-xl font-bold text-pivote">{resultado.expresion}</p>
        </div>
      )}
    </div>
  );
}

function FormaParametrica({ solucion, letra }) {
  const { forma_parametrica: forma, forma_vectorial: vectorial } = solucion;
  return (
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
          <span className="font-display text-lg font-bold">{letra} =</span>
          <VectorColumna vector={vectorial.particular} />
          {vectorial.direcciones.map((d) => (
            <span key={d.parametro} className="flex items-center gap-2">
              <Operador>+</Operador>
              <span className="font-mono text-lg font-bold text-pivote">{d.parametro}</span>
              <VectorColumna vector={d.vector} />
            </span>
          ))}
        </div>
        <p className="mt-3 font-mono text-sm text-grafito">
          {letra} = {textoVector(vectorial.particular)}
          {vectorial.direcciones.map(
            (d) => ` + ${d.parametro}·${textoVector(d.vector)}`
          )}
        </p>
      </div>
    </div>
  );
}

function SinVerificacion() {
  return (
    <div className="math-empty-verification">
      <div className="math-empty-icon">∅</div>
      <div>
        <p className="font-display text-lg font-bold">No hay solución que comprobar</p>
        <p className="mt-1 text-sm text-grafito">
          Un sistema inconsistente no tiene valores que se puedan sustituir.
        </p>
      </div>
    </div>
  );
}

function Veredicto({ coincide, texto }) {
  return (
    <div
      className={`rounded-xl border px-4 py-3 text-sm font-semibold ${
        coincide
          ? "border-determinado/25 bg-determinado/10 text-determinado"
          : "border-inconsistente/25 bg-inconsistente/10 text-inconsistente"
      }`}
    >
      {coincide ? `✓ ${texto}` : "✗ No coincide"}
    </div>
  );
}

function VerificacionCombinacion({ resultado }) {
  const verificacion = resultado.verificaciones[0];
  if (!verificacion) return <SinVerificacion />;

  return (
    <div className="space-y-4">
      <p className="text-sm text-grafito">
        Se recalcula Σ cᵢ·vᵢ con las operaciones de ℝⁿ y se compara con b.
      </p>
      <div className="p3-lienzo">
        {verificacion.terminos.map((t, j) => (
          <span key={j} className="flex items-center gap-2">
            {j > 0 && <Operador>+</Operador>}
            <span className="font-mono text-lg font-bold text-pivote">{t.peso.fraccion}</span>
            <VectorColumna vector={t.vector} />
          </span>
        ))}
        <Operador>=</Operador>
        <VectorColumna vector={verificacion.recalculado} />
        <Operador>{verificacion.coincide ? "=" : "≠"}</Operador>
        <span className="flex items-center gap-2">
          <span className="font-display text-lg font-bold">b</span>
          <VectorColumna vector={verificacion.esperado} />
        </span>
      </div>
      <p className="font-mono text-sm">
        Σ cᵢ·vᵢ = {textoVector(verificacion.recalculado)} · b ={" "}
        {textoVector(verificacion.esperado)}
      </p>
      <Veredicto coincide={verificacion.coincide} texto="Coinciden: la combinación es correcta." />
    </div>
  );
}

function VerificacionEcuacion({ resultado }) {
  if (resultado.verificaciones.length === 0) return <SinVerificacion />;

  // A = matriz inicial sin la última columna (solo se recortan filas de texto).
  const A = resultado.matriz_inicial.map((fila) => fila.slice(0, -1));

  return (
    <div className="space-y-6">
      <p className="text-sm text-grafito">
        Se calcula A·x con la misma función de producto matricial y se compara con b.
      </p>
      {resultado.verificaciones.map((v) => (
        <div key={v.etiqueta} className="space-y-3">
          <p className="font-display text-sm font-semibold text-pivote">{v.etiqueta}</p>
          <div className="p3-lienzo">
            <span className="font-display text-lg font-bold">A</span>
            <MatrizEstatica matriz={A} aumentada={false} />
            <Operador>·</Operador>
            <VectorColumna vector={v.x} />
            <Operador>=</Operador>
            <VectorColumna vector={v.Ax} />
            <Operador>{v.coincide ? "=" : "≠"}</Operador>
            <span className="flex items-center gap-2">
              <span className="font-display text-lg font-bold">b</span>
              <VectorColumna vector={v.b} />
            </span>
          </div>
          <Veredicto coincide={v.coincide} texto="A·x = b" />
        </div>
      ))}
    </div>
  );
}
