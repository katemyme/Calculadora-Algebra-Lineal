// Opción 11 del Programa 3: verificar A(u + v) = A·u + A·v con u, v ∈ ℝⁿ.
//
// u y v siempre tienen tantas componentes como columnas de A, así que su
// tamaño sigue al de A. Ambos lados los calcula el backend por separado.

import { useState } from "react";
import { programa3 } from "../../lib/api.js";
import Boton from "../ui/Boton.jsx";
import MatrizEstatica from "../MatrizEstatica.jsx";
import { SelectorOrden } from "./SeccionMatrices.jsx";
import {
  AvisoError,
  BloqueMatriz,
  Cargando,
  EditorMatriz,
  Operador,
  TarjetaResultado,
  VectorColumna,
  cambiarCelda,
  celdaConError,
  redimensionarVector,
  textoVector,
  useOperacion,
} from "./comunes.jsx";

const CASOS = [
  {
    nombre: "A 2×3, u y v ∈ ℝ³",
    A: [["1", "2", "3"], ["0", "-1", "4"]],
    u: ["1", "0", "2"],
    v: ["1/2", "3", "-1"],
  },
  {
    nombre: "A 3×3",
    A: [["2", "1", "-1"], ["-3", "-1", "2"], ["-2", "1", "2"]],
    u: ["1", "2", "3"],
    v: ["-1", "0", "4"],
  },
  {
    nombre: "A 3×2, u y v ∈ ℝ²",
    A: [["1", "-2"], ["0", "5"], ["3", "1"]],
    u: ["2", "-1"],
    v: ["0.5", "4"],
  },
];

// Un vector ℝⁿ se edita como matriz columna n×1.
const aColumna = (vector) => vector.map((valor) => [valor]);

export default function SeccionDistributiva() {
  const [A, setA] = useState(CASOS[0].A.map((f) => [...f]));
  const [u, setU] = useState([...CASOS[0].u]);
  const [v, setV] = useState([...CASOS[0].v]);
  const { resultado, error, cargando, ejecutar, limpiar } = useOperacion();

  const m = A.length;
  const n = A[0].length;

  function cargarCaso(caso) {
    setA(caso.A.map((f) => [...f]));
    setU([...caso.u]);
    setV([...caso.v]);
    limpiar();
  }

  function cambiarOrden(nueva) {
    setA(nueva);
    setU(redimensionarVector(u, nueva[0].length));
    setV(redimensionarVector(v, nueva[0].length));
    limpiar();
  }

  const editorVector = (nombre, valores, fijar) => (
    <BloqueMatriz nombre={nombre} orden={`ℝ${superindice(n)}`}>
      <EditorMatriz
        etiqueta={nombre}
        valores={aColumna(valores)}
        onCambiar={(i, _j, texto) => {
          fijar(valores.map((valor, k) => (k === i ? texto : valor)));
          limpiar();
        }}
        celdaError={celdaConError(error, nombre)}
        compacta
      />
    </BloqueMatriz>
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap gap-2">
        {CASOS.map((caso) => (
          <Boton key={caso.nombre} variante="secundario" className="text-xs" onClick={() => cargarCaso(caso)}>
            {caso.nombre}
          </Boton>
        ))}
      </div>

      <div className="space-y-3">
        <SelectorOrden nombre="A" matriz={A} onCambiar={cambiarOrden} />
        <span className="p3-dim p3-dim-ok">
          A es {m}×{n} → u y v deben estar en ℝ{superindice(n)} (tantas componentes como columnas de A)
        </span>
      </div>

      <div className="p3-lienzo">
        <BloqueMatriz nombre="A" orden={`${m}×${n}`}>
          <EditorMatriz
            etiqueta="A"
            valores={A}
            onCambiar={(i, j, texto) => {
              setA(cambiarCelda(A, i, j, texto));
              limpiar();
            }}
            celdaError={celdaConError(error, "A")}
            compacta
          />
        </BloqueMatriz>
        {editorVector("u", u, setU)}
        {editorVector("v", v, setV)}
      </div>

      <Boton onClick={() => ejecutar(() => programa3.distributiva({ A, u, v }))} disabled={cargando}>
        {cargando ? "Verificando…" : "Verificar A(u + v) = A·u + A·v"}
      </Boton>

      {cargando && <Cargando texto="Verificando…" />}
      <AvisoError error={error} />
      {resultado && <ResultadoDistributiva resultado={resultado} />}
    </div>
  );
}

function superindice(numero) {
  const digitos = "⁰¹²³⁴⁵⁶⁷⁸⁹";
  return String(numero)
    .split("")
    .map((d) => digitos[Number(d)])
    .join("");
}

function Lado({ titulo, children, texto, nombre }) {
  return (
    <div className="math-form-card space-y-4">
      <p className="font-display text-base font-bold text-tinta">{titulo}</p>
      <div className="flex flex-wrap items-center gap-3 overflow-x-auto">{children}</div>
      <p className="font-mono text-sm font-semibold text-determinado">
        {nombre} = {texto}
      </p>
    </div>
  );
}

function ResultadoDistributiva({ resultado }) {
  const { A, dimensiones, coincide } = resultado;
  const matrizA = (
    <BloqueMatriz orden={`A ${dimensiones.A}`}>
      <MatrizEstatica matriz={A} aumentada={false} />
    </BloqueMatriz>
  );

  return (
    <TarjetaResultado titulo="Propiedad distributiva" formula="A(u + v) = A·u + A·v">
      <div className="space-y-5">
        <Lado titulo="Lado izquierdo: A(u + v)" nombre="A(u + v)" texto={textoVector(resultado.izquierda)}>
          <VectorColumna vector={resultado.u} />
          <Operador>+</Operador>
          <VectorColumna vector={resultado.v} />
          <Operador>=</Operador>
          <VectorColumna vector={resultado.u_mas_v} />
          <span className="font-mono text-xs text-grafito">= u + v</span>
        </Lado>
        <div className="-mt-2 flex flex-wrap items-center gap-3 overflow-x-auto pl-5">
          {matrizA}
          <Operador>·</Operador>
          <VectorColumna vector={resultado.u_mas_v} />
          <Operador>=</Operador>
          <div className="rounded-xl bg-determinado/10 p-1">
            <VectorColumna vector={resultado.izquierda} />
          </div>
        </div>

        <Lado titulo="Lado derecho: A·u + A·v" nombre="A·u + A·v" texto={textoVector(resultado.derecha)}>
          {matrizA}
          <Operador>·</Operador>
          <VectorColumna vector={resultado.u} />
          <Operador>=</Operador>
          <VectorColumna vector={resultado.Au} />
          <span className="mx-2" />
          {matrizA}
          <Operador>·</Operador>
          <VectorColumna vector={resultado.v} />
          <Operador>=</Operador>
          <VectorColumna vector={resultado.Av} />
        </Lado>
        <div className="-mt-2 flex flex-wrap items-center gap-3 overflow-x-auto pl-5">
          <VectorColumna vector={resultado.Au} />
          <Operador>+</Operador>
          <VectorColumna vector={resultado.Av} />
          <Operador>=</Operador>
          <div className="rounded-xl bg-determinado/10 p-1">
            <VectorColumna vector={resultado.derecha} />
          </div>
        </div>

        <div
          className={`math-solution-banner ${coincide ? "" : "math-solution-error"}`}
          style={{ animation: "aparecer-paso 0.3s ease both" }}
        >
          <div
            className="math-solution-icon"
            style={{ color: coincide ? "var(--determinado)" : "var(--inconsistente)" }}
          >
            {coincide ? "✓" : "✗"}
          </div>
          <div>
            <p className={`font-display text-lg font-bold ${coincide ? "text-determinado" : "text-inconsistente"}`}>
              {coincide ? "A(u + v) = A·u + A·v" : "A(u + v) ≠ A·u + A·v"}
            </p>
            <p className="mt-1 text-sm text-tinta">
              {coincide
                ? "Ambos lados dan el mismo vector: se cumple la propiedad distributiva."
                : "Los dos lados no coinciden."}
            </p>
          </div>
        </div>
      </div>
    </TarjetaResultado>
  );
}
