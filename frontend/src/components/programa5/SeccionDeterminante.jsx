// Opción 6 del Programa 5: det(A) por tres métodos, cada uno en su propia pestaña de
// «Álgebra de Matrices» y con su solución paso a paso:
//
//   · Cofactores: expansión sobre la fila 1 (vale para cualquier n, cuesta ≈ n!),
//   · Regla de Sarrus: solo 3×3,
//   · Triangular: reducción a forma triangular (el método eficiente, ≈ n³).
//
// Las tres pestañas comparten la matriz y el resultado: el backend calcula los tres
// métodos en una sola llamada y cada pestaña presenta el desarrollo del suyo. Al final
// de cada una se comprueba que los métodos coinciden.

import { createContext, useContext, useState } from "react";
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
import PasosPorCofactores, { ETAPAS_COFACTORES } from "./DeterminantePorCofactores.jsx";
import PasosPorReduccion, { ETAPAS_REDUCCION } from "./DeterminantePorReduccion.jsx";
import PasosPorSarrus, { ETAPAS_SARRUS } from "./DeterminantePorSarrus.jsx";
import {
  BotonesDeCasos,
  Diagnostico,
  EditorNombrado,
  PlanDePasos,
  SelectorOrdenN,
  copiarRejilla,
} from "./comunes.jsx";

const CASOS = [
  { nombre: "Invertible 3×3", A: [["1", "2", "3"], ["0", "1", "4"], ["5", "6", "0"]] },
  { nombre: "Singular 3×3", A: [["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"]] },
  { nombre: "Pivote 0 (3×3)", A: [["0", "2", "1"], ["1", "1", "0"], ["2", "0", "1"]] },
  { nombre: "Pivote 0 (2×2)", A: [["0", "2"], ["3", "4"]] },
  { nombre: "Con fracciones", A: [["1/2", "-0.5"], ["3/4", "2"]] },
  {
    nombre: "Matriz 4×4",
    A: [
      ["1", "2", "0", "1"],
      ["2", "5", "1", "3"],
      ["0", "1", "3", "2"],
      ["1", "3", "2", "5"],
    ],
  },
];

const ORDEN_DE_SARRUS = 3;

// Lo propio de cada pestaña: textos, etapas y el componente que pinta su paso a paso.
const METODOS = {
  cofactores: {
    nombre: "Cofactores",
    titulo: "Determinante por cofactores",
    pistas: ["det A = Σ a₁ⱼ·C₁ⱼ", "Cᵢⱼ = (−1)ⁱ⁺ʲ·det Mᵢⱼ", "Mᵢⱼ = A sin la fila i ni la columna j"],
    cargando: "Calculando cada menor y su cofactor…",
    etapas: ETAPAS_COFACTORES,
    Pasos: PasosPorCofactores,
  },
  sarrus: {
    nombre: "Sarrus",
    titulo: "Determinante por la regla de Sarrus",
    pistas: ["solo matrices 3×3", "det A = (suma de diagonales ↘) − (suma de diagonales ↗)"],
    cargando: "Calculando los productos de las diagonales…",
    etapas: ETAPAS_SARRUS,
    Pasos: PasosPorSarrus,
  },
  triangular: {
    nombre: "Triangular",
    titulo: "Determinante por reducción a forma triangular",
    pistas: [
      "triangular ⇒ det = producto de la diagonal",
      "Fᵢ ↔ Fⱼ cambia el signo",
      "Fᵢ → Fᵢ − k·Fⱼ no altera det",
    ],
    cargando: "Reduciendo A a forma triangular…",
    etapas: ETAPAS_REDUCCION,
    Pasos: PasosPorReduccion,
  },
};

const ContextoDeterminante = createContext(null);

/** Guarda la matriz y el resultado que comparten las tres pestañas del determinante. */
export function ProveedorDeterminante({ children }) {
  const [A, setA] = useState(() => copiarRejilla(CASOS[0].A));
  const operacion = useOperacion();

  function fijarA(nueva) {
    setA(nueva);
    operacion.limpiar();
  }

  const calcular = () => operacion.ejecutar(() => programa5.determinante({ A }));

  return (
    <ContextoDeterminante.Provider value={{ A, fijarA, calcular, ...operacion }}>
      {children}
    </ContextoDeterminante.Provider>
  );
}

export default function SeccionDeterminante({ metodo }) {
  const { A, fijarA, calcular, resultado, error, cargando } = useContext(ContextoDeterminante);
  const definicion = METODOS[metodo];
  const n = A.length;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <SelectorOrdenN
          id={`p5-det-${metodo}-n`}
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
        {definicion.pistas.map((pista) => (
          <span key={pista}>{pista}</span>
        ))}
      </div>

      <div className="p3-lienzo">
        <Operador>det</Operador>
        <EditorNombrado nombre="A" matriz={A} onCambiar={fijarA} error={error} soloCuadrada />
        <Operador>=</Operador>
        <span className="font-display text-3xl text-grafito/50">?</span>
      </div>

      <p className="text-xs text-grafito">
        La matriz es la misma en las pestañas «Cofactores», «Regla de Sarrus» y «Triangular»:
        se calcula una vez y cada pestaña muestra el paso a paso de su método.
      </p>

      {metodo === "sarrus" && n !== ORDEN_DE_SARRUS && (
        <p className="math-note">
          La regla de Sarrus solo vale para matrices 3×3 y esta es {n}×{n}. Cambie el orden a
          3 o use las pestañas «Cofactores» o «Triangular».
        </p>
      )}

      <Boton onClick={calcular} disabled={cargando}>
        {cargando ? "Calculando…" : "Calcular determinante"}
      </Boton>

      {cargando && <Cargando texto={definicion.cargando} />}
      <AvisoError error={error} />
      {resultado && (
        <ResultadoDeterminante
          key={JSON.stringify(resultado.A)}
          resultado={resultado}
          metodo={metodo}
        />
      )}
    </div>
  );
}

function ResultadoDeterminante({ resultado, metodo }) {
  const { titulo, etapas, Pasos } = METODOS[metodo];
  const aplicable = metodo !== "sarrus" || Boolean(resultado.sarrus);

  return (
    <TarjetaResultado
      titulo={titulo}
      formula={aplicable ? `det(A) = ${textoFraccion(resultado.determinante)}` : "solo para matrices 3×3"}
    >
      <div className="space-y-5">
        {aplicable && <PlanDePasos etapas={etapas} />}
        <Pasos resultado={resultado} />
        <ComparacionDeMetodos resultado={resultado} />
        <Diagnostico diagnostico={resultado.diagnostico} />
      </div>
    </TarjetaResultado>
  );
}

/** El valor que dio cada método y si coinciden (lo decide el backend). */
function ComparacionDeMetodos({ resultado }) {
  const { cofactores, sarrus, reduccion, coinciden } = resultado;
  const valores = [
    { nombre: "Cofactores", valor: textoFraccion(cofactores.valor) },
    { nombre: "Sarrus", valor: sarrus ? textoFraccion(sarrus.valor) : "no se aplica" },
    { nombre: "Triangular", valor: textoFraccion(reduccion.valor) },
  ];

  return (
    <div className={`math-solution-banner ${coinciden ? "math-solution-ok" : "math-solution-error"}`}>
      <div
        className="math-solution-icon"
        style={{ color: `var(--${coinciden ? "determinado" : "inconsistente"})` }}
      >
        {coinciden ? "=" : "≠"}
      </div>
      <div className="min-w-0 space-y-2">
        <p
          className={`font-display text-lg font-bold ${
            coinciden ? "text-determinado" : "text-inconsistente"
          }`}
        >
          {coinciden
            ? `Los métodos coinciden: det(A) = ${textoFraccion(resultado.determinante)}`
            : "Los métodos no coinciden"}
        </p>
        <div className="flex flex-wrap gap-2">
          {valores.map(({ nombre, valor }) => (
            <span key={nombre} className="math-param-chip">
              {nombre}: {valor}
            </span>
          ))}
        </div>
        <p className="text-sm text-tinta">
          Cada método se calculó por separado, con fracciones exactas. El desarrollo de los
          otros está en sus pestañas.
        </p>
      </div>
    </div>
  );
}
