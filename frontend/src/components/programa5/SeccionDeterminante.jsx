// Opción 6 del Programa 5: det(A) por tres métodos que deben coincidir.
//
//   a) expansión por cofactores (vale para cualquier n, cuesta ≈ n!),
//   b) regla de Sarrus (solo 3×3),
//   c) reducción a forma triangular (el método eficiente, ≈ n³).
//
// Los tres valores y el diagnóstico los calcula el backend; aquí se presentan.

import { useState } from "react";
import { programa5 } from "../../lib/api.js";
import { textoFraccion } from "../../lib/formato.js";
import Boton from "../ui/Boton.jsx";
import {
  AvisoError,
  Cargando,
  Operador,
  TarjetaResultado,
  redimensionarRejilla,
  useOperacion,
} from "../programa3/comunes.jsx";
import {
  BotonesDeCasos,
  Diagnostico,
  EditorNombrado,
  ReduccionTriangular,
  SelectorOrdenN,
  TarjetaNumerada,
  copiarRejilla,
} from "./comunes.jsx";

const CASOS = [
  { nombre: "Invertible 3×3", A: [["1", "2", "3"], ["0", "1", "4"], ["5", "6", "0"]] },
  { nombre: "Singular 3×3", A: [["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"]] },
  { nombre: "Pivote 0 (2×2)", A: [["0", "2"], ["3", "4"]] },
  { nombre: "Con fracciones", A: [["1/2", "-0.5"], ["3/4", "2"]] },
];

export default function SeccionDeterminante() {
  const [A, setA] = useState(() => copiarRejilla(CASOS[0].A));
  const { resultado, error, cargando, ejecutar, limpiar } = useOperacion();
  const n = A.length;

  function fijarA(nueva) {
    setA(nueva);
    limpiar();
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <SelectorOrdenN
          id="p5-det-n"
          valor={n}
          onCambiar={(orden) => fijarA(redimensionarRejilla(A, orden, orden))}
        />
        <BotonesDeCasos
          casos={CASOS}
          onCargar={(caso) => fijarA(copiarRejilla(caso.A))}
          onLimpiar={() => fijarA(redimensionarRejilla([], n, n))}
        />
      </div>

      <div className="math-formula-strip" aria-hidden="true">
        <span>det A = Σ a₁ⱼ·C₁ⱼ</span>
        <span>Cᵢⱼ = (−1)ⁱ⁺ʲ·det Mᵢⱼ</span>
        <span>triangular ⇒ det = producto de la diagonal</span>
      </div>

      <div className="p3-lienzo">
        <Operador>det</Operador>
        <EditorNombrado nombre="A" matriz={A} onCambiar={fijarA} error={error} />
        <Operador>=</Operador>
        <span className="font-display text-3xl text-grafito/50">?</span>
      </div>

      <Boton onClick={() => ejecutar(() => programa5.determinante({ A }))} disabled={cargando}>
        {cargando ? "Calculando…" : "Calcular determinante"}
      </Boton>

      {cargando && <Cargando texto="Calculando det(A) por los tres métodos…" />}
      <AvisoError error={error} />
      {resultado && <ResultadoDeterminante resultado={resultado} />}
    </div>
  );
}

function ResultadoDeterminante({ resultado }) {
  const { cofactores, sarrus, reduccion, coinciden } = resultado;
  const determinante = textoFraccion(resultado.determinante);

  return (
    <TarjetaResultado titulo="Determinante" formula={`det(A) = ${determinante}`}>
      <div className="space-y-5">
        <TarjetaNumerada numero="a" titulo="Expansión por cofactores" nota="≈ n! multiplicaciones">
          <p className="text-sm text-grafito">
            Cada entrada de la fila 1 por su cofactor{" "}
            <span className="font-semibold text-pivote">C₁ⱼ</span>.
          </p>
          <p className="font-mono text-sm leading-7">
            det(A) ={" "}
            {cofactores.terminos.map((termino, columna) => (
              <span key={columna}>
                {columna > 0 && " + "}({textoFraccion(termino.entrada)})·
                <span className="font-semibold text-pivote">
                  ({textoFraccion(termino.cofactor)})
                </span>
              </span>
            ))}{" "}
            = <strong>{textoFraccion(cofactores.valor)}</strong>
          </p>
        </TarjetaNumerada>

        <TarjetaNumerada numero="b" titulo="Regla de Sarrus" nota="solo 3×3">
          {sarrus ? (
            <div className="space-y-1 font-mono text-sm">
              <p>Diagonales descendentes (↘): {textoFraccion(sarrus.descendentes)}</p>
              <p>Diagonales ascendentes (↗): {textoFraccion(sarrus.ascendentes)}</p>
              <p>
                det(A) = ({textoFraccion(sarrus.descendentes)}) − (
                {textoFraccion(sarrus.ascendentes)}) ={" "}
                <strong>{textoFraccion(sarrus.valor)}</strong>
              </p>
            </div>
          ) : (
            <p className="text-sm text-grafito">
              No se aplica: la regla de Sarrus solo vale para matrices 3×3 y esta es{" "}
              {resultado.n}×{resultado.n}.
            </p>
          )}
        </TarjetaNumerada>

        <TarjetaNumerada
          numero="c"
          titulo="Reducción a forma triangular"
          nota="método eficiente · ≈ n³ operaciones"
        >
          <ReduccionTriangular reduccion={reduccion} />
        </TarjetaNumerada>

        <div
          className={`math-solution-banner ${
            coinciden ? "math-solution-ok" : "math-solution-error"
          }`}
        >
          <div
            className="math-solution-icon"
            style={{ color: `var(--${coinciden ? "determinado" : "inconsistente"})` }}
          >
            {coinciden ? "=" : "≠"}
          </div>
          <div>
            <p
              className={`font-display text-lg font-bold ${
                coinciden ? "text-determinado" : "text-inconsistente"
              }`}
            >
              {coinciden
                ? `Los métodos coinciden: det(A) = ${determinante}`
                : "Los métodos no coinciden"}
            </p>
            <p className="mt-1 text-sm text-tinta">
              Cofactores{sarrus ? ", Sarrus" : ""} y reducción triangular se calcularon por
              separado, con fracciones exactas.
            </p>
          </div>
        </div>

        <Diagnostico diagnostico={resultado.diagnostico} />
      </div>
    </TarjetaResultado>
  );
}
