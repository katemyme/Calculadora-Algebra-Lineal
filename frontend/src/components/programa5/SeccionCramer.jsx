// Regla de Cramer (pestaña Álgebra de Matrices): xᵢ = det Aᵢ(b) / det A.
//
// Envía A (n×n) y el vector b. El backend
// ("backend/programa_4/modulos/modulo_determinantes.py") devuelve det A, cada
// matriz Aᵢ(b) con su determinante, los cocientes xᵢ y la comprobación A·x = b;
// aquí solo se pintan, paso a paso.
//
// NOTA DE CUMPLIMIENTO: no hay álgebra en este archivo. Lo único que se cuenta
// son filas y columnas de la rejilla.

import { useState } from "react";
import { determinantes } from "../../lib/api.js";
import { textoFraccion } from "../../lib/formato.js";
import Boton from "../ui/Boton.jsx";
import {
  AvisoError,
  BloqueMatriz,
  Cargando,
  EditorMatriz,
  Operador,
  TarjetaResultado,
  VectorColumna,
  celdaConError,
  redimensionarRejilla,
  redimensionarVector,
  textoVector,
  useOperacion,
} from "../programa3/comunes.jsx";
import { EcuacionesDeSustitucion } from "../programa6/SeccionLU.jsx";
import { BotonCopiarMatriz } from "../programa6/portapapeles.jsx";
import {
  BotonesDeCasos,
  EditorNombrado,
  ExpansionPorCofactores,
  MatrizNombrada,
  ReduccionTriangular,
  SelectorOrdenN,
  TarjetaNumerada,
  Veredicto,
  copiarRejilla,
} from "./comunes.jsx";

const CASOS = [
  { nombre: "Sistema 2×2", A: [["3", "-2"], ["-5", "4"]], b: ["6", "8"] },
  {
    nombre: "Sistema 3×3",
    A: [["2", "1", "-1"], ["-3", "-1", "2"], ["-2", "1", "2"]],
    b: ["8", "-11", "-3"],
  },
  { nombre: "Con fracciones", A: [["2", "1"], ["1", "3"]], b: ["1/2", "2"] },
  {
    nombre: "Sistema 4×4",
    A: [
      ["1", "2", "0", "1"],
      ["2", "5", "1", "3"],
      ["0", "1", "3", "2"],
      ["1", "3", "2", "5"],
    ],
    b: ["-1", "-1", "5", "2"],
  },
  { nombre: "det A = 0 (sin solución)", A: [["1", "2"], ["2", "4"]], b: ["3", "5"] },
  { nombre: "det A = 0 (no decide)", A: [["1", "2"], ["2", "4"]], b: ["3", "6"] },
];

// Hasta este orden los desarrollos de los determinantes se muestran abiertos; con
// matrices mayores ocupan mucho y se abren a petición.
const ORDEN_MAXIMO_DESPLEGADO = 3;

// Un vector se edita y se dibuja como matriz columna n×1.
const aColumna = (vector) => vector.map((valor) => [valor]);

export default function SeccionCramer() {
  const [A, setA] = useState(() => copiarRejilla(CASOS[0].A));
  const [b, setB] = useState(() => [...CASOS[0].b]);
  const { resultado, error, cargando, ejecutar, limpiar } = useOperacion();
  const n = A.length;

  // b tiene una componente por fila de A: se ajusta cada vez que A cambia de tamaño
  // (también al pegar una matriz copiada de otra sección).
  function fijarA(nueva) {
    setA(nueva);
    setB(redimensionarVector(b, nueva.length));
    limpiar();
  }

  function cargarCaso(caso) {
    setA(copiarRejilla(caso.A));
    setB([...caso.b]);
    limpiar();
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <SelectorOrdenN
          id="cramer-n"
          valor={n}
          onCambiar={(orden) => fijarA(redimensionarRejilla(A, orden, orden))}
        />
        <BotonesDeCasos
          casos={CASOS}
          onCargar={cargarCaso}
          onLimpiar={() => {
            setA(redimensionarRejilla([], n, n));
            setB(redimensionarVector([], n));
            limpiar();
          }}
        />
      </div>

      <div className="math-formula-strip" aria-hidden="true">
        <span>xᵢ = det Aᵢ(b) / det A</span>
        <span>i = 1, 2, …, n</span>
        <span>Aᵢ(b) = A con la columna i reemplazada por b</span>
      </div>

      <div className="p3-lienzo">
        <EditorNombrado nombre="A" matriz={A} onCambiar={fijarA} error={error} soloCuadrada />
        <Operador>· x =</Operador>
        <BloqueMatriz nombre="b" orden={`${n}×1`}>
          <EditorMatriz
            etiqueta="b"
            valores={aColumna(b)}
            onCambiar={(i, _j, texto) => {
              setB(b.map((valor, k) => (k === i ? texto : valor)));
              limpiar();
            }}
            celdaError={celdaConError(error, "b")}
            compacta
          />
        </BloqueMatriz>
      </div>

      <p className="text-xs text-grafito">
        A debe ser cuadrada (n ecuaciones, n incógnitas). Acepta enteros, decimales y
        fracciones (3, -0.5, 3/2). Celda vacía = 0.
      </p>

      <Boton
        onClick={() => ejecutar(() => determinantes.cramer({ A, b }))}
        disabled={cargando}
      >
        {cargando ? "Resolviendo…" : "Resolver Ax = b por la Regla de Cramer"}
      </Boton>

      {cargando && <Cargando texto="Calculando det A y cada det Aᵢ(b)…" />}
      <AvisoError error={error} />
      {resultado && <ResultadoCramer key={JSON.stringify(resultado.A)} resultado={resultado} />}
    </div>
  );
}

function ResultadoCramer({ resultado }) {
  const { aplicable } = resultado;

  return (
    <TarjetaResultado
      titulo="Regla de Cramer"
      formula={aplicable ? `x = ${textoVector(resultado.x)}` : "det A = 0: sin solución única"}
    >
      <div className="space-y-5">
        <PlanDeSolucion />
        <Planteamiento resultado={resultado} />
        <DeterminanteDeA resultado={resultado} />
        <MatricesDeCramer resultado={resultado} />
        {aplicable ? (
          <>
            <Cocientes resultado={resultado} />
            <ComprobacionFinal resultado={resultado} />
          </>
        ) : (
          <SinSolucionUnica resultado={resultado} />
        )}
      </div>
    </TarjetaResultado>
  );
}

/** Mapa del procedimiento, para que el usuario sepa qué va a ver y en qué orden. */
function PlanDeSolucion() {
  const etapas = [
    "Plantear Ax = b",
    "Calcular det A",
    "Armar cada Aᵢ(b) y su determinante",
    "Dividir: xᵢ = det Aᵢ(b) / det A",
    "Comprobar A·x = b",
  ];

  return (
    <ol className="flex flex-wrap items-center gap-2" aria-label="Pasos del procedimiento">
      {etapas.map((etapa, indice) => (
        <li key={etapa} className="math-param-chip">
          {indice + 1}. {etapa}
        </li>
      ))}
    </ol>
  );
}

/** Paso 1: el sistema en forma matricial y lo que dice la regla. */
function Planteamiento({ resultado }) {
  const { incognitas, n } = resultado;
  const nombres = incognitas.map((incognita) => incognita.variable).join(", ");

  return (
    <TarjetaNumerada numero="1" titulo="Plantear el sistema Ax = b" nota={`${n} incógnitas`}>
      <div className="flex flex-wrap items-center gap-3 overflow-x-auto">
        <MatrizNombrada nombre="A" matriz={resultado.A} />
        <Operador>· x =</Operador>
        <MatrizNombrada nombre="b" matriz={aColumna(resultado.b)} />
      </div>
      <p className="text-sm text-grafito">
        A guarda los coeficientes, b los términos independientes y x las incógnitas{" "}
        <span className="font-mono">{nombres}</span>. La Regla de Cramer halla cada incógnita
        con un cociente de determinantes:{" "}
        <span className="font-mono font-semibold text-pivote">xᵢ = det Aᵢ(b) / det A</span>,
        donde <span className="font-mono">Aᵢ(b)</span> es la matriz A con su columna i
        reemplazada por b.
      </p>
    </TarjetaNumerada>
  );
}

/** Desarrollo de un determinante: por cofactores o por reducción, según lo envíe el backend. */
function DesarrolloDeterminante({ desarrollo }) {
  if (desarrollo.tipo === "det_cofactores") {
    return <ExpansionPorCofactores procedimiento={desarrollo} />;
  }
  return <ReduccionTriangular reduccion={desarrollo.reduccion} nombre={desarrollo.nombre} pasoAPaso />;
}

/** Desarrollo de un determinante que se puede plegar; `abierto` fija cómo empieza. */
function DesarrolloPlegable({ desarrollo, nombre, abierto }) {
  const [visible, setVisible] = useState(abierto);

  return (
    <div className="space-y-3">
      <Boton
        variante="secundario"
        className="text-xs"
        aria-expanded={visible}
        onClick={() => setVisible((previo) => !previo)}
      >
        {visible ? `Ocultar el cálculo de det ${nombre}` : `Ver cómo se calcula det ${nombre}`}
      </Boton>
      {visible && (
        <div className="space-y-3" style={{ animation: "aparecer-paso 0.3s ease both" }}>
          <p className="text-xs text-grafito">{desarrollo.titulo}</p>
          <DesarrolloDeterminante desarrollo={desarrollo} />
        </div>
      )}
    </div>
  );
}

/** Paso 2: det A, que decide si la regla se puede aplicar. */
function DeterminanteDeA({ resultado }) {
  const { aplicable } = resultado;
  const determinante = textoFraccion(resultado.det_A);

  return (
    <TarjetaNumerada numero="2" titulo="Calcular det A" nota="el denominador de todas las xᵢ">
      <p className="text-sm text-grafito">
        det A divide en todas las fórmulas, así que se calcula primero: la regla solo sirve si{" "}
        <strong>det A ≠ 0</strong>.
      </p>
      <DesarrolloDeterminante desarrollo={resultado.desarrollo_A} />
      <div className="flex flex-wrap items-center gap-2">
        <span className="math-param-chip">det A = {determinante}</span>
        <Veredicto cumple={aplicable}>
          {aplicable
            ? "det A ≠ 0: A es invertible y el sistema tiene solución única"
            : "det A = 0: la regla no se puede aplicar"}
        </Veredicto>
      </div>
    </TarjetaNumerada>
  );
}

/** Paso 3: por cada incógnita, A con la columna i cambiada por b y su determinante. */
function MatricesDeCramer({ resultado }) {
  const { incognitas, n } = resultado;
  const abierto = n <= ORDEN_MAXIMO_DESPLEGADO;

  return (
    <TarjetaNumerada
      numero="3"
      titulo="Armar cada Aᵢ(b) y calcular su determinante"
      nota={`${n} ${n === 1 ? "matriz" : "matrices"}, una por incógnita`}
    >
      <p className="text-sm text-grafito">
        Para la incógnita xᵢ se copia A y se cambia <strong>solo la columna i</strong> por el
        vector b (resaltada en azul); las demás columnas quedan igual.
      </p>
      <ol className="space-y-4">
        {incognitas.map((incognita) => (
          <MatrizDeIncognita
            key={incognita.variable}
            incognita={incognita}
            A={resultado.A}
            abierto={abierto}
          />
        ))}
      </ol>
    </TarjetaNumerada>
  );
}

/** A → Aᵢ(b) para una incógnita, con el determinante de Aᵢ(b) y su desarrollo. */
function MatrizDeIncognita({ incognita, A, abierto }) {
  const { indice, variable, nombre_matriz: nombre, matriz, determinante, desarrollo } = incognita;

  return (
    <li className="space-y-3 rounded-xl border border-[var(--borde)] bg-white p-4">
      <p className="font-display text-sm font-bold text-tinta">
        <span className="text-pivote">Para {variable}.</span> Se reemplaza la columna{" "}
        {indice + 1} de A por b
      </p>
      <div className="flex flex-wrap items-center gap-x-4 gap-y-3 overflow-x-auto">
        <MatrizNombrada nombre="A" matriz={A} columnaDestacada={indice} />
        <div className="flex flex-col items-center text-pivote">
          <span className="font-display text-xs font-semibold">columna {indice + 1} ← b</span>
          <span className="text-2xl leading-none">⟶</span>
        </div>
        <MatrizNombrada nombre={nombre} matriz={matriz} columnaDestacada={indice} />
        <span className="math-param-chip">
          det {nombre} = {textoFraccion(determinante)}
        </span>
      </div>
      <DesarrolloPlegable desarrollo={desarrollo} nombre={nombre} abierto={abierto} />
    </li>
  );
}

/** Paso 4: cada xᵢ como cociente y el vector solución. */
function Cocientes({ resultado }) {
  const { incognitas, x } = resultado;
  const determinante = textoFraccion(resultado.det_A);

  return (
    <TarjetaNumerada numero="4" titulo="Dividir: xᵢ = det Aᵢ(b) / det A">
      <p className="text-sm text-grafito">
        Cada determinante del paso 3 se divide entre{" "}
        <span className="font-mono">det A = {determinante}</span> (paso 2).
      </p>
      <EcuacionesDeSustitucion ecuaciones={incognitas.map((incognita) => incognita.ecuacion)} />
      <div className="flex flex-wrap items-center gap-3">
        <span className="font-display text-lg font-bold text-tinta">x =</span>
        <div className="rounded-xl bg-determinado/10 p-1">
          <VectorColumna vector={x} />
        </div>
        <span className="text-xs text-grafito">solución única del sistema Ax = b</span>
        <BotonCopiarMatriz matriz={aColumna(x)} nombre="x" />
      </div>
    </TarjetaNumerada>
  );
}

/** Paso 5: el backend multiplica A·x y lo compara con b. */
function ComprobacionFinal({ resultado }) {
  const { x, b, comprobacion } = resultado;

  return (
    <TarjetaNumerada numero="5" titulo="Comprobar la solución en el sistema original">
      <div className="flex flex-wrap items-center gap-3 overflow-x-auto">
        <MatrizNombrada nombre="A" matriz={resultado.A} />
        <Operador>·</Operador>
        <MatrizNombrada nombre="x" matriz={aColumna(x)} />
        <Operador>=</Operador>
        <MatrizNombrada nombre="A·x" matriz={aColumna(comprobacion.Ax)} />
        <Operador>{comprobacion.correcta ? "=" : "≠"}</Operador>
        <MatrizNombrada nombre="b" matriz={aColumna(b)} />
      </div>
      <Veredicto cumple={comprobacion.correcta}>{comprobacion.mensaje}</Veredicto>
    </TarjetaNumerada>
  );
}

/** det A = 0: no se puede dividir; se explica qué se sabe del sistema. */
function SinSolucionUnica({ resultado }) {
  return (
    <div className="math-solution-banner math-solution-error">
      <div className="math-solution-icon" style={{ color: "var(--inconsistente)" }}>∄</div>
      <div className="min-w-0 space-y-2">
        <p className="font-display text-lg font-bold text-inconsistente">
          La Regla de Cramer no se puede aplicar
        </p>
        <p className="text-sm text-tinta">
          El paso 4 pediría dividir entre det A = 0. Cuando det A = 0 la matriz A no es
          invertible y el sistema <strong>no tiene solución única</strong>.
        </p>
        <p className="text-sm text-tinta">{resultado.motivo}</p>
        <p className="text-sm text-grafito">
          Para clasificarlo y ver su solución general use la pestaña «Sistemas de Ecuaciones
          Lineales» (Gauss-Jordan).
        </p>
      </div>
    </div>
  );
}
