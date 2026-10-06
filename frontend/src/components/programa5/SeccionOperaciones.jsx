// Opciones 1 a 5 del Programa 5: A + B, A − B, k·A, A·B y Aᵀ.
//
// La vista avisa de las dimensiones antes de calcular, pero quien valida y
// explica el error es el backend (p. ej. "Columnas de A [3] ≠ Filas de B [2]").

import { useState } from "react";
import { programa5 } from "../../lib/api.js";
import { textoFraccion } from "../../lib/formato.js";
import Boton from "../ui/Boton.jsx";
import { SelectorOrden } from "../programa3/SeccionMatrices.jsx";
import {
  AvisoError,
  Cargando,
  Operador,
  SelectorOperacion,
  TarjetaResultado,
  celdaConError,
  redimensionarRejilla,
  useOperacion,
} from "../programa3/comunes.jsx";
import {
  BotonesDeCasos,
  CampoTexto,
  EditorNombrado,
  MatrizNombrada,
  copiarRejilla,
  ordenDe,
} from "./comunes.jsx";

const OPERACIONES = [
  { id: "suma", etiqueta: "A + B", simbolo: "+", usaB: true, formula: "(A + B)ᵢⱼ = aᵢⱼ + bᵢⱼ" },
  { id: "resta", etiqueta: "A − B", simbolo: "−", usaB: true, formula: "(A − B)ᵢⱼ = aᵢⱼ − bᵢⱼ" },
  { id: "escalar", etiqueta: "k · A", simbolo: "·", usaB: false, formula: "(kA)ᵢⱼ = k·aᵢⱼ" },
  { id: "producto", etiqueta: "A · B", simbolo: "·", usaB: true, formula: "cᵢⱼ = Σₖ aᵢₖ·bₖⱼ" },
  { id: "transpuesta", etiqueta: "Aᵀ", simbolo: "ᵀ", usaB: false, formula: "(Aᵀ)ᵢⱼ = aⱼᵢ" },
];

const MATRIZ_2X3 = [["1", "2", "3"], ["4", "5", "6"]];

const CASOS = [
  {
    nombre: "A·C (2×3 · 3×2)",
    operacion: "producto",
    A: MATRIZ_2X3,
    B: [["1", "0"], ["2", "1"], ["0", "3"]],
  },
  { nombre: "Error 2×3 · 2×3", operacion: "producto", A: MATRIZ_2X3, B: MATRIZ_2X3 },
  {
    nombre: "Suma con fracciones",
    operacion: "suma",
    A: [["1", "2"], ["3", "4"]],
    B: [["1/2", "-0.5"], ["0", "3/2"]],
  },
  { nombre: "Escalar 3/2", operacion: "escalar", A: [["1", "2"], ["3", "4"]], k: "3/2" },
  { nombre: "Transpuesta 2×3", operacion: "transpuesta", A: MATRIZ_2X3 },
];

/** Nombre de la matriz resultado: "A + B", "(3/2)·A", "Aᵀ", … */
function nombreDelResultado(resultado) {
  if (resultado.operacion === "escalar") return `(${textoFraccion(resultado.k)})·A`;
  return OPERACIONES.find((operacion) => operacion.id === resultado.operacion).etiqueta;
}

export default function SeccionOperaciones() {
  const [operacion, setOperacion] = useState("suma");
  const [A, setA] = useState(() => redimensionarRejilla([], 2, 2));
  const [B, setB] = useState(() => redimensionarRejilla([], 2, 2));
  const [k, setK] = useState("2");
  const { resultado, error, cargando, ejecutar, limpiar } = useOperacion();

  const definicion = OPERACIONES.find((opcion) => opcion.id === operacion);
  const esEscalar = operacion === "escalar";

  // Envuelve un setter para descartar el resultado anterior al cambiar un dato.
  const alCambiar = (fijar) => (valor) => {
    fijar(valor);
    limpiar();
  };

  function cargarCaso(caso) {
    setOperacion(caso.operacion);
    setA(copiarRejilla(caso.A));
    if (caso.B) setB(copiarRejilla(caso.B));
    if (caso.k) setK(caso.k);
    limpiar();
  }

  function limpiarRejillas() {
    setA(redimensionarRejilla([], A.length, A[0].length));
    setB(redimensionarRejilla([], B.length, B[0].length));
    limpiar();
  }

  function calcular() {
    ejecutar(() =>
      programa5.operacion({
        operacion,
        A,
        B: definicion.usaB ? B : [],
        k: esEscalar ? k : null,
      })
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <SelectorOperacion
          opciones={OPERACIONES}
          activa={operacion}
          onCambiar={alCambiar(setOperacion)}
        />
        <BotonesDeCasos casos={CASOS} onCargar={cargarCaso} onLimpiar={limpiarRejillas} />
      </div>

      <div className="space-y-3">
        <SelectorOrden nombre="A" matriz={A} onCambiar={alCambiar(setA)} />
        {definicion.usaB && <SelectorOrden nombre="B" matriz={B} onCambiar={alCambiar(setB)} />}
        <AvisoDeDimensiones operacion={operacion} A={A} B={B} />
      </div>

      <div className="p3-lienzo">
        {esEscalar && (
          <>
            <CampoTexto
              etiqueta="k"
              descripcion="Escalar k"
              valor={k}
              onCambiar={alCambiar(setK)}
              conError={celdaConError(error, "k") !== null}
            />
            <Operador>·</Operador>
          </>
        )}
        <EditorNombrado nombre="A" matriz={A} onCambiar={alCambiar(setA)} error={error} />
        {operacion === "transpuesta" && <Operador>ᵀ</Operador>}
        {definicion.usaB && (
          <>
            <Operador>{definicion.simbolo}</Operador>
            <EditorNombrado nombre="B" matriz={B} onCambiar={alCambiar(setB)} error={error} />
          </>
        )}
        <Operador>=</Operador>
        <span className="font-display text-3xl text-grafito/50">?</span>
      </div>

      <p className="text-xs text-grafito">
        Acepta enteros, decimales y fracciones (3, -0.5, 3/2). Celda vacía = 0.
      </p>

      <Boton onClick={calcular} disabled={cargando}>
        {cargando ? "Calculando…" : `Calcular ${definicion.etiqueta}`}
      </Boton>

      {cargando && <Cargando />}
      <AvisoError error={error} />
      {resultado && <ResultadoOperacion resultado={resultado} />}
    </div>
  );
}

/** Píldora que anticipa si las dimensiones admiten la operación elegida. */
function AvisoDeDimensiones({ operacion, A, B }) {
  if (operacion === "suma" || operacion === "resta") {
    const iguales = ordenDe(A) === ordenDe(B);
    return (
      <span className={`p3-dim ${iguales ? "p3-dim-ok" : "p3-dim-mal"}`}>
        A <strong>{ordenDe(A)}</strong> · B <strong>{ordenDe(B)}</strong>
        {iguales ? " → misma dimensión ✓" : " → dimensiones distintas ✗"}
      </span>
    );
  }
  if (operacion === "producto") {
    const columnasA = A[0].length;
    const filasB = B.length;
    const compatible = columnasA === filasB;
    return (
      <span className={`p3-dim ${compatible ? "p3-dim-ok" : "p3-dim-mal"}`}>
        A {A.length}×<strong>{columnasA}</strong> · B <strong>{filasB}</strong>×{B[0].length}
        {compatible
          ? ` → columnas(A) = filas(B) ✓  A·B será ${A.length}×${B[0].length}`
          : ` → columnas(A) = ${columnasA} ≠ filas(B) = ${filasB} ✗`}
      </span>
    );
  }
  return null;
}

function ResultadoOperacion({ resultado }) {
  const definicion = OPERACIONES.find((opcion) => opcion.id === resultado.operacion);

  return (
    <TarjetaResultado titulo={`Resultado (${resultado.dimension})`} formula={definicion.formula}>
      <div className="space-y-5">
        <div className="flex flex-wrap items-center gap-3 overflow-x-auto">
          {resultado.operacion === "escalar" && (
            <>
              <span className="font-mono text-xl font-bold">{textoFraccion(resultado.k)}</span>
              <Operador>·</Operador>
            </>
          )}
          <MatrizNombrada nombre="A" matriz={resultado.A} />
          {resultado.operacion === "transpuesta" && <Operador>ᵀ</Operador>}
          {definicion.usaB && (
            <>
              <Operador>{definicion.simbolo}</Operador>
              <MatrizNombrada nombre="B" matriz={resultado.B} />
            </>
          )}
          <Operador>=</Operador>
          <MatrizNombrada
            nombre={nombreDelResultado(resultado)}
            matriz={resultado.resultado}
            destacada
          />
        </div>

        {resultado.conmutatividad && <Conmutatividad datos={resultado.conmutatividad} />}
      </div>
    </TarjetaResultado>
  );
}

/** Tras A·B: muestra B·A si existe y deja claro que el producto no conmuta. */
function Conmutatividad({ datos }) {
  if (!datos.definido) {
    return (
      <p className="math-note">
        <strong>B·A no está definido</strong> (las columnas de B no coinciden con las filas
        de A): el producto matricial no es conmutativo.
      </p>
    );
  }
  return (
    <div className="space-y-3">
      <p className="font-display text-base font-bold text-tinta">En el otro orden: B·A</p>
      <div className="flex overflow-x-auto">
        <MatrizNombrada nombre="B·A" matriz={datos.BA} />
      </div>
      <p className="math-note">
        {datos.iguales ? (
          <>En este caso <strong>A·B = B·A</strong>, pero en general el producto no conmuta.</>
        ) : (
          <>
            <strong>A·B ≠ B·A</strong>: el producto matricial no es conmutativo.
          </>
        )}
      </p>
    </div>
  );
}
