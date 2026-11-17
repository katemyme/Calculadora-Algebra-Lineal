// Vista principal del Programa 8: Jacobi y Gauss-Seidel.
// Captura A (n×n), b, x^(0), tolerancia ε, Nmax y opción de reordenamiento,
// permite cargar los 3 casos de prueba obligatorios y presenta diagnóstico,
// tablas, gráfica comparativa y validación contra solución de referencia.

import { useEffect, useState } from "react";
import {
  programa8,
  ErrorDeCalculo,
  ErrorDeServidor,
} from "../../lib/api.js";
import Boton from "../ui/Boton.jsx";
import Panel from "../ui/Panel.jsx";
import GraficaError from "./GraficaError.jsx";
import TablaIteraciones, { formatearNumero } from "./TablaIteraciones.jsx";

const DIMENSION_MINIMA = 1;
const DIMENSION_MAXIMA = 8;
const SUBINDICES = ["₁", "₂", "₃", "₄", "₅", "₆", "₇", "₈"];

const subindice = (i) => SUBINDICES[i] ?? `_${i + 1}`;
const matrizVacia = (n) =>
  Array.from({ length: n }, () => Array.from({ length: n }, () => ""));
const vectorVacio = (n, defecto = "") =>
  Array.from({ length: n }, () => defecto);

// Respaldo local de los 3 casos obligatorios por si aún no responde GET /api/p8/ejemplos
const CASOS_RESPALDO = [
  {
    id: "caso1_convergencia",
    nombre: "Caso 1 · Convergencia (Matriz estrictamente diagonal dominante)",
    descripcion:
      "Sistema 3×3 estrictamente diagonal dominante por filas. Ambos métodos convergen a la solución exacta x = [2, 4, 3]ᵀ, observándose que Gauss-Seidel requiere menos iteraciones que Jacobi.",
    A: [
      ["4", "-1", "1"],
      ["4", "-8", "1"],
      ["-2", "1", "5"],
    ],
    b: ["7", "-21", "15"],
    x0: ["0", "0", "0"],
    tolerancia: "1e-5",
    max_iter: "50",
    permitir_reordenamiento: true,
  },
  {
    id: "caso2_reordenamiento",
    nombre: "Caso 2 · Reordenamiento de filas (Cero en la diagonal inicial)",
    descripcion:
      "Sistema 3×3 con cero en la diagonal inicial (a₁₁ = 0). El intercambio de filas permite converger a x = [1, 2, 3]ᵀ.",
    A: [
      ["0", "5", "-1"],
      ["4", "1", "-1"],
      ["1", "-1", "6"],
    ],
    b: ["7", "3", "17"],
    x0: ["0", "0", "0"],
    tolerancia: "1e-5",
    max_iter: "50",
    permitir_reordenamiento: true,
  },
  {
    id: "caso3_no_convergencia",
    nombre: "Caso 3 · Advertencia / No convergencia (Sin dominancia diagonal)",
    descripcion:
      "Sistema 3×3 invertible (det(A) = 4, solución exacta x = [1, 1, 1]ᵀ) que no cumple la condición suficiente de diagonal dominante bajo ningún reordenamiento posible. Ambos métodos divergen y el programa detiene el cálculo con advertencia clara sin cerrarse.",
    A: [
      ["1", "4", "4"],
      ["1", "2", "4"],
      ["1", "4", "2"],
    ],
    b: ["9", "7", "7"],
    x0: ["0", "0", "0"],
    tolerancia: "1e-4",
    max_iter: "30",
    permitir_reordenamiento: true,
  },
];

export default function ProgramaIterativos() {
  const [n, setN] = useState(3);
  const [A, setA] = useState(CASOS_RESPALDO[0].A);
  const [b, setB] = useState(CASOS_RESPALDO[0].b);
  const [x0, setX0] = useState(CASOS_RESPALDO[0].x0);
  const [tolerancia, setTolerancia] = useState("1e-5");
  const [maxIter, setMaxIter] = useState("50");
  const [permitirReordenamiento, setPermitirReordenamiento] = useState(true);

  const [casos, setCasos] = useState(CASOS_RESPALDO);
  const [casoActivo, setCasoActivo] = useState(CASOS_RESPALDO[0]);
  const [resultado, setResultado] = useState(null);
  const [error, setError] = useState(null);
  const [cargando, setCargando] = useState(false);

  useEffect(() => {
    programa8
      .ejemplos()
      .then((datos) => {
        if (datos?.casos?.length) {
          setCasos(datos.casos);
          setCasoActivo(datos.casos[0]);
        }
      })
      .catch(() => {
        // Conserva CASOS_RESPALDO si el backend aún no está levantado
      });
  }, []);

  function limpiarSalida() {
    setResultado(null);
    setError(null);
  }

  function cambiarDimension(nuevoN) {
    setN(nuevoN);
    setA((prev) =>
      Array.from({ length: nuevoN }, (_, i) =>
        Array.from({ length: nuevoN }, (_, j) => prev[i]?.[j] ?? "")
      )
    );
    setB((prev) => Array.from({ length: nuevoN }, (_, i) => prev[i] ?? ""));
    setX0((prev) => Array.from({ length: nuevoN }, (_, i) => prev[i] ?? "0"));
    setCasoActivo(null);
    limpiarSalida();
  }

  function actualizarCeldaA(i, j, valor) {
    setA((prev) =>
      prev.map((fila, r) =>
        r === i ? fila.map((celda, c) => (c === j ? valor : celda)) : fila
      )
    );
    limpiarSalida();
  }

  function actualizarVector(setter, idx, valor) {
    setter((prev) => prev.map((item, i) => (i === idx ? valor : item)));
    limpiarSalida();
  }

  function cargarCaso(caso) {
    const dim = caso.A.length;
    setN(dim);
    setA(caso.A.map((fila) => [...fila]));
    setB([...caso.b]);
    setX0([...caso.x0]);
    setTolerancia(caso.tolerancia);
    setMaxIter(caso.max_iter);
    setPermitirReordenamiento(caso.permitir_reordenamiento ?? true);
    setCasoActivo(caso);
    limpiarSalida();
  }

  function limpiarFormulario() {
    setA(matrizVacia(n));
    setB(vectorVacio(n, ""));
    setX0(vectorVacio(n, "0"));
    setCasoActivo(null);
    limpiarSalida();
  }

  async function calcular() {
    setCargando(true);
    setError(null);
    setResultado(null);

    try {
      const datos = await programa8.iterativos({
        A,
        b,
        x0,
        tolerancia,
        max_iter: maxIter,
        permitir_reordenamiento: permitirReordenamiento,
      });
      setResultado(datos);
    } catch (ex) {
      setError(ex);
    } finally {
      setCargando(false);
    }
  }

  const celdaErrorA =
    error instanceof ErrorDeCalculo && error.campo === "A" && error.fila
      ? { fila: error.fila - 1, columna: (error.columna ?? 1) - 1 }
      : null;

  const filaErrorB =
    error instanceof ErrorDeCalculo && error.campo === "b" && error.fila
      ? error.fila - 1
      : null;

  const filaErrorX0 =
    error instanceof ErrorDeCalculo && error.campo === "x0" && error.fila
      ? error.fila - 1
      : null;

  return (
    <div className="space-y-7">
      {/* PANEL DE ENTRADA */}
      <Panel
        className="math-panel overflow-hidden"
        titulo="Configuración del sistema Ax = b"
        descripcion="Introduce la matriz cuadrada A (n×n), el vector b, el vector inicial x⁽⁰⁾, la tolerancia ε y el límite de iteraciones."
        acciones={
          <Boton
            variante="fantasma"
            className="text-xs"
            onClick={limpiarFormulario}
          >
            Limpiar
          </Boton>
        }
      >
        <div className="space-y-6">
          {/* Controles superiores: Dimensión, Tolerancia, Nmax y Reordenamiento */}
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div>
              <label className="block text-xs font-semibold text-grafito">
                Orden de A (n × n)
              </label>
              <select
                value={n}
                onChange={(e) => cambiarDimension(Number(e.target.value))}
                className="mt-1.5 w-full rounded-xl border border-[var(--borde)] bg-white px-3 py-2 text-sm text-tinta focus:border-indigo-500 focus:outline-none"
              >
                {Array.from(
                  { length: DIMENSION_MAXIMA - DIMENSION_MINIMA + 1 },
                  (_, idx) => DIMENSION_MINIMA + idx
                ).map((dim) => (
                  <option key={dim} value={dim}>
                    {dim} × {dim} ({dim} incógnitas)
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-grafito">
                Tolerancia (ε &gt; 0)
              </label>
              <input
                type="text"
                value={tolerancia}
                onChange={(e) => {
                  setTolerancia(e.target.value);
                  limpiarSalida();
                }}
                placeholder="1e-5"
                className={`mt-1.5 w-full rounded-xl border bg-white px-3 py-2 font-mono text-sm text-tinta focus:outline-none ${
                  error instanceof ErrorDeCalculo &&
                  error.campo === "tolerancia"
                    ? "border-inconsistente ring-2 ring-inconsistente/20"
                    : "border-[var(--borde)] focus:border-indigo-500"
                }`}
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-grafito">
                Máx. iteraciones (Nmax)
              </label>
              <input
                type="text"
                value={maxIter}
                onChange={(e) => {
                  setMaxIter(e.target.value);
                  limpiarSalida();
                }}
                placeholder="50"
                className={`mt-1.5 w-full rounded-xl border bg-white px-3 py-2 font-mono text-sm text-tinta focus:outline-none ${
                  error instanceof ErrorDeCalculo && error.campo === "max_iter"
                    ? "border-inconsistente ring-2 ring-inconsistente/20"
                    : "border-[var(--borde)] focus:border-indigo-500"
                }`}
              />
            </div>

            <div className="flex items-end pb-1">
              <label className="flex cursor-pointer items-center gap-2.5 text-xs font-medium text-tinta">
                <input
                  type="checkbox"
                  checked={permitirReordenamiento}
                  onChange={(e) => {
                    setPermitirReordenamiento(e.target.checked);
                    limpiarSalida();
                  }}
                  className="h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
                />
                <span>Permitir reordenar filas (ceros / dominancia)</span>
              </label>
            </div>
          </div>

          {/* Rejillas de A, b y x^(0) */}
          <div className="overflow-x-auto pb-2">
            <div className="inline-flex min-w-full flex-wrap items-start gap-6">
              {/* Matriz A */}
              <div>
                <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-grafito">
                  Matriz de coeficientes A ({n}×{n})
                </p>
                <div className="inline-grid gap-2 rounded-2xl border border-[var(--borde)] bg-slate-50/70 p-3">
                  {A.map((fila, i) => (
                    <div key={i} className="flex items-center gap-2">
                      {fila.map((valor, j) => {
                        const esDiagonal = i === j;
                        const tieneError =
                          celdaErrorA?.fila === i && celdaErrorA?.columna === j;
                        return (
                          <input
                            key={j}
                            type="text"
                            value={valor}
                            onChange={(e) =>
                              actualizarCeldaA(i, j, e.target.value)
                            }
                            aria-label={`A[${i + 1},${j + 1}]`}
                            placeholder={`a${subindice(i)}${subindice(j)}`}
                            className={`h-10 w-16 rounded-lg border px-2 text-center font-mono text-sm transition focus:outline-none sm:w-20 ${
                              tieneError
                                ? "border-inconsistente bg-inconsistente/5 ring-2 ring-inconsistente/25"
                                : esDiagonal
                                  ? "border-indigo-300 bg-indigo-50/40 font-semibold text-tinta focus:border-indigo-600"
                                  : "border-[var(--borde)] bg-white text-tinta focus:border-indigo-500"
                            }`}
                          />
                        );
                      })}
                    </div>
                  ))}
                </div>
              </div>

              {/* Vector b */}
              <div>
                <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-grafito">
                  Vector b
                </p>
                <div className="inline-grid gap-2 rounded-2xl border border-[var(--borde)] bg-slate-50/70 p-3">
                  {b.map((valor, i) => (
                    <input
                      key={i}
                      type="text"
                      value={valor}
                      onChange={(e) =>
                        actualizarVector(setB, i, e.target.value)
                      }
                      aria-label={`b[${i + 1}]`}
                      placeholder={`b${subindice(i)}`}
                      className={`h-10 w-20 rounded-lg border px-2 text-center font-mono text-sm transition focus:outline-none ${
                        filaErrorB === i
                          ? "border-inconsistente bg-inconsistente/5 ring-2 ring-inconsistente/25"
                          : "border-[var(--borde)] bg-white text-tinta focus:border-indigo-500"
                      }`}
                    />
                  ))}
                </div>
              </div>

              {/* Vector inicial x^(0) */}
              <div>
                <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-grafito">
                  Vector inicial x⁽⁰⁾
                </p>
                <div className="inline-grid gap-2 rounded-2xl border border-[var(--borde)] bg-slate-50/70 p-3">
                  {x0.map((valor, i) => (
                    <input
                      key={i}
                      type="text"
                      value={valor}
                      onChange={(e) =>
                        actualizarVector(setX0, i, e.target.value)
                      }
                      aria-label={`x0[${i + 1}]`}
                      placeholder={`x${subindice(i)}⁽⁰⁾`}
                      className={`h-10 w-20 rounded-lg border px-2 text-center font-mono text-sm transition focus:outline-none ${
                        filaErrorX0 === i
                          ? "border-inconsistente bg-inconsistente/5 ring-2 ring-inconsistente/25"
                          : "border-[var(--borde)] bg-white text-tinta focus:border-indigo-500"
                      }`}
                    />
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Botón principal de cálculo */}
          <div className="flex flex-wrap items-center gap-3">
            <Boton onClick={calcular} disabled={cargando}>
              {cargando
                ? "Calculando iteraciones…"
                : "Resolver por Jacobi y Gauss-Seidel"}
            </Boton>
            {error && (
              <p className="text-sm text-inconsistente">
                {error instanceof ErrorDeServidor
                  ? "Error de conexión con el servidor."
                  : error.message}
              </p>
            )}
          </div>

          {/* Descripción del caso activo y botones Caso 1, 2 y 3 debajo del botón principal */}
          <div className="space-y-3 border-t border-[var(--borde)] pt-5">
            {casoActivo && (
              <div className="rounded-xl border border-indigo-200/80 bg-indigo-50/60 p-3.5 text-xs text-slate-700">
                <p className="font-semibold text-indigo-950">
                  {casoActivo.nombre}
                </p>
                <p className="mt-1 leading-5">{casoActivo.descripcion}</p>
              </div>
            )}

            <div className="flex flex-wrap items-center gap-2">
              {casos.map((caso, idx) => (
                <Boton
                  key={caso.id}
                  variante="secundario"
                  className={`text-xs ${
                    casoActivo?.id === caso.id
                      ? "border-indigo-400 bg-indigo-50/70 text-indigo-950"
                      : ""
                  }`}
                  onClick={() => cargarCaso(caso)}
                >
                  {`Caso ${idx + 1}`}
                </Boton>
              ))}
            </div>
          </div>
        </div>
      </Panel>

      {/* CARGANDO */}
      {cargando && (
        <Panel className="math-panel" titulo="Procesando">
          <div className="flex items-center gap-3 text-grafito">
            <span className="math-loader" aria-hidden="true" />
            Evaluando dominancia diagonal y ejecutando Jacobi y Gauss-Seidel…
          </div>
        </Panel>
      )}

      {/* RESULTADOS */}
      {resultado && !cargando && (
        <div className="space-y-7">
          {/* 1. Diagnóstico de diagonal y dominancia */}
          <Panel
            className="math-panel"
            titulo="1. Diagnóstico previo: Diagonal y Dominancia por filas"
            descripcion="Verifica ceros en la diagonal, reordenamiento de filas y condición suficiente de convergencia."
          >
            <div className="space-y-4">
              {/* Reordenamiento */}
              <div
                className={`rounded-xl border p-3.5 text-sm ${
                  !resultado.ejecutado
                    ? "border-inconsistente/30 bg-inconsistente/5 text-inconsistente"
                    : resultado.reordenamiento.reordenado
                      ? "border-amber-200 bg-amber-50/80 text-amber-950"
                      : "border-[var(--borde)] bg-slate-50/70 text-tinta"
                }`}
              >
                <p className="font-semibold">Estado de la diagonal y filas:</p>
                <p className="mt-1">{resultado.reordenamiento.mensaje}</p>
              </div>

              {/* Si hubo reordenamiento, mostrar el sistema equivalente [A | b] usado */}
              {resultado.reordenamiento.reordenado && (
                <div className="rounded-xl border border-[var(--borde)] bg-white p-3.5">
                  <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-grafito">
                    Sistema equivalente reordenado utilizado para iterar [A′ | b′]
                  </p>
                  <div className="overflow-x-auto font-mono text-xs">
                    <table className="divide-y divide-slate-200">
                      <tbody>
                        {resultado.A_utilizada.map((fila, i) => (
                          <tr key={i}>
                            {fila.map((val, j) => (
                              <td
                                key={j}
                                className={`px-3 py-1.5 text-right ${
                                  i === j
                                    ? "font-bold text-indigo-700"
                                    : "text-tinta"
                                }`}
                              >
                                {formatearNumero(val, 6)}
                              </td>
                            ))}
                            <td className="border-l-2 border-slate-400 px-3 py-1.5 font-semibold text-tinta">
                              {formatearNumero(resultado.b_utilizada[i], 6)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Dominancia estricta */}
              <div
                className={`rounded-xl border p-3.5 text-sm ${
                  resultado.dominancia.es_estrictamente_dominante
                    ? "border-emerald-200 bg-emerald-50/70 text-emerald-950"
                    : "border-amber-200 bg-amber-50/70 text-amber-950"
                }`}
              >
                <p className="font-semibold">
                  {resultado.dominancia.es_estrictamente_dominante
                    ? "✓ Matriz estrictamente diagonal dominante por filas"
                    : "⚠ Matriz NO estrictamente diagonal dominante por filas"}
                </p>
                <p className="mt-1 leading-6">
                  {resultado.dominancia.mensaje}
                </p>
              </div>

              {/* Desglose fila por fila */}
              <div className="overflow-x-auto rounded-xl border border-[var(--borde)]">
                <table className="min-w-full divide-y divide-[var(--borde)] text-left text-xs">
                  <thead className="bg-slate-100 text-grafito">
                    <tr>
                      <th className="px-3 py-2 font-semibold">Fila i</th>
                      <th className="px-3 py-2 font-semibold">|aᵢᵢ|</th>
                      <th className="px-3 py-2 font-semibold">
                        Σ |aᵢⱼ| (j ≠ i)
                      </th>
                      <th className="px-3 py-2 font-semibold">Condición</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 bg-white font-mono">
                    {resultado.dominancia.filas.map((f) => (
                      <tr key={f.fila}>
                        <td className="px-3 py-2 font-semibold">
                          Fila {f.fila}
                        </td>
                        <td className="px-3 py-2">
                          {formatearNumero(f.diagonal_abs, 6)}
                        </td>
                        <td className="px-3 py-2">
                          {formatearNumero(f.suma_otros_abs, 6)}
                        </td>
                        <td className="px-3 py-2 font-sans">
                          {f.cumple ? (
                            <span className="font-semibold text-emerald-700">
                              ✓ |aᵢᵢ| &gt; Σ|aᵢⱼ|
                            </span>
                          ) : (
                            <span className="font-semibold text-amber-700">
                              ✗ |aᵢᵢ| ≤ Σ|aᵢⱼ|
                            </span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </Panel>

          {/* 2. Comparación y Validación contra referencia exacta */}
          {resultado.ejecutado && (
            <Panel
              className="math-panel"
              titulo="2. Comparación y Validación con solución de referencia"
              descripcion="Contrasta el rendimiento de Jacobi frente a Gauss-Seidel y verifica la precisión frente a la solución exacta."
            >
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2 rounded-xl border border-[var(--borde)] bg-slate-50/80 p-4 text-sm">
                  <p className="text-xs font-semibold uppercase tracking-wider text-grafito">
                    Comparación Jacobi vs. Gauss-Seidel
                  </p>
                  <p className="font-medium text-tinta">
                    {resultado.comparacion.resumen}
                  </p>
                  <div className="pt-1 text-xs text-grafito">
                    <p>
                      • Iteraciones Jacobi:{" "}
                      <strong className="text-tinta">
                        {resultado.comparacion.iteraciones_jacobi}
                      </strong>
                    </p>
                    <p>
                      • Iteraciones Gauss-Seidel:{" "}
                      <strong className="text-tinta">
                        {resultado.comparacion.iteraciones_gauss_seidel}
                      </strong>
                    </p>
                    {resultado.comparacion.diferencia_soluciones_inf !==
                      null && (
                      <p>
                        • Diferencia ||x_Jacobi − x_GS||∞:{" "}
                        <strong className="font-mono text-tinta">
                          {resultado.comparacion.diferencia_soluciones_inf.toExponential(
                            4
                          )}
                        </strong>
                      </p>
                    )}
                  </div>
                </div>

                <div className="space-y-2 rounded-xl border border-[var(--borde)] bg-slate-50/80 p-4 text-sm">
                  <p className="text-xs font-semibold uppercase tracking-wider text-grafito">
                    Validación con solución exacta
                  </p>
                  {resultado.validacion_referencia?.disponible ? (
                    <>
                      <p className="text-xs text-grafito">
                        Referencia:{" "}
                        <code>
                          {resultado.validacion_referencia.metodo_referencia}
                        </code>
                      </p>
                      <p className="font-mono text-sm font-semibold text-tinta">
                        x_exacta = (
                        {resultado.validacion_referencia.solucion_referencia
                          .map(
                            (v, i) =>
                              `x${subindice(i)} = ${formatearNumero(v, 7)}`
                          )
                          .join(",  ")}
                        )
                      </p>
                      <div className="pt-1 text-xs text-grafito">
                        {resultado.validacion_referencia.diferencia_jacobi !==
                          null && (
                          <p>
                            • ||x_Jacobi − x_exacta||∞:{" "}
                            <strong className="font-mono text-tinta">
                              {resultado.validacion_referencia.diferencia_jacobi.toExponential(
                                4
                              )}
                            </strong>
                          </p>
                        )}
                        {resultado.validacion_referencia
                          .diferencia_gauss_seidel !== null && (
                          <p>
                            • ||x_GaussSeidel − x_exacta||∞:{" "}
                            <strong className="font-mono text-tinta">
                              {resultado.validacion_referencia.diferencia_gauss_seidel.toExponential(
                                4
                              )}
                            </strong>
                          </p>
                        )}
                      </div>
                    </>
                  ) : (
                    <p className="text-sm text-amber-800">
                      {resultado.validacion_referencia?.motivo ??
                        "No se pudo calcular la solución exacta de referencia."}
                    </p>
                  )}
                </div>
              </div>
            </Panel>
          )}

          {/* 3. Gráfica comparativa del error */}
          {resultado.ejecutado && resultado.grafica_error?.disponible && (
            <Panel
              className="math-panel"
              titulo="3. Gráfica comparativa del error"
              descripcion="Evolución de ||x⁽ᵏ⁾ − x⁽ᵏ⁻¹⁾||∞ para Jacobi y Gauss-Seidel."
            >
              <GraficaError grafica={resultado.grafica_error} />
            </Panel>
          )}

          {/* 4. Tablas de iteraciones individuales */}
          {resultado.ejecutado && (
            <div className="grid gap-7 lg:grid-cols-2">
              <TablaIteraciones datos={resultado.jacobi} />
              <TablaIteraciones datos={resultado.gauss_seidel} />
            </div>
          )}
        </div>
      )}
    </div>
  );
}