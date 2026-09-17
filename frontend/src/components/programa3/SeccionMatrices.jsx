// Opciones 5, 6 y 7 del Programa 3: A + B, A − B y c·A.

import { useState } from "react";
import { programa3 } from "../../lib/api.js";
import Boton from "../ui/Boton.jsx";
import SelectorDimension from "../ui/SelectorDimension.jsx";
import MatrizEstatica from "../MatrizEstatica.jsx";
import {
  AvisoError,
  BloqueMatriz,
  Cargando,
  DIMENSION_MAXIMA,
  DIMENSION_MINIMA,
  EditorMatriz,
  Operador,
  SelectorOperacion,
  TarjetaResultado,
  cambiarCelda,
  celdaConError,
  redimensionarRejilla,
  useOperacion,
} from "./comunes.jsx";

const OPERACIONES = [
  { id: "suma", etiqueta: "A + B", simbolo: "+" },
  { id: "resta", etiqueta: "A − B", simbolo: "−" },
  { id: "escalar", etiqueta: "c · A", simbolo: "·" },
];

const CASOS = [
  {
    nombre: "Suma 2×2",
    operacion: "suma",
    A: [["1", "2"], ["3", "4"]],
    B: [["5", "6"], ["7", "8"]],
  },
  {
    nombre: "Resta 2×2",
    operacion: "resta",
    A: [["5", "6"], ["7", "8"]],
    B: [["1", "2"], ["3", "4"]],
  },
  { nombre: "Escalar 0.5", operacion: "escalar", c: "0.5", A: [["2", "-4"], ["1", "3"]] },
  {
    nombre: "Órdenes distintos",
    operacion: "suma",
    A: [["1", "2"], ["3", "4"]],
    B: [["1", "2"], ["3", "4"], ["5", "6"]],
  },
];

const orden = (matriz) => `${matriz.length}×${matriz[0].length}`;

export function SelectorOrden({ nombre, matriz, onCambiar }) {
  return (
    <div className="flex flex-wrap items-center gap-x-5 gap-y-2">
      <span className="font-display text-sm font-bold">{nombre}</span>
      <SelectorDimension
        id={`filas-${nombre}`}
        etiqueta="filas"
        valor={matriz.length}
        minimo={DIMENSION_MINIMA}
        maximo={DIMENSION_MAXIMA}
        onCambiar={(filas) => onCambiar(redimensionarRejilla(matriz, filas, matriz[0].length))}
      />
      <SelectorDimension
        id={`columnas-${nombre}`}
        etiqueta="columnas"
        valor={matriz[0].length}
        minimo={DIMENSION_MINIMA}
        maximo={DIMENSION_MAXIMA}
        onCambiar={(columnas) => onCambiar(redimensionarRejilla(matriz, matriz.length, columnas))}
      />
    </div>
  );
}

export default function SeccionMatrices() {
  const [operacion, setOperacion] = useState("suma");
  const [A, setA] = useState(redimensionarRejilla([], 2, 2));
  const [B, setB] = useState(redimensionarRejilla([], 2, 2));
  const [c, setC] = useState("2");
  const { resultado, error, cargando, ejecutar, limpiar } = useOperacion();

  const esEscalar = operacion === "escalar";
  const simbolo = OPERACIONES.find((o) => o.id === operacion).simbolo;
  const mismoOrden = orden(A) === orden(B);

  function cargarCaso(caso) {
    setOperacion(caso.operacion);
    setA(caso.A.map((f) => [...f]));
    if (caso.B) setB(caso.B.map((f) => [...f]));
    if (caso.c) setC(caso.c);
    limpiar();
  }

  function calcular() {
    ejecutar(() =>
      programa3.matrices({ operacion, A, B: esEscalar ? [] : B, c: esEscalar ? c : null })
    );
  }

  const editor = (nombre, matriz, fijar) => (
    <BloqueMatriz nombre={nombre} orden={orden(matriz)}>
      <EditorMatriz
        etiqueta={nombre}
        valores={matriz}
        onCambiar={(i, j, texto) => {
          fijar(cambiarCelda(matriz, i, j, texto));
          limpiar();
        }}
        celdaError={celdaConError(error, nombre)}
        compacta
      />
    </BloqueMatriz>
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <SelectorOperacion
          opciones={OPERACIONES}
          activa={operacion}
          onCambiar={(id) => {
            setOperacion(id);
            limpiar();
          }}
        />
        <div className="flex flex-wrap gap-2">
          {CASOS.map((caso) => (
            <Boton key={caso.nombre} variante="secundario" className="text-xs" onClick={() => cargarCaso(caso)}>
              {caso.nombre}
            </Boton>
          ))}
        </div>
      </div>

      <div className="space-y-3">
        <SelectorOrden nombre="A" matriz={A} onCambiar={(m) => { setA(m); limpiar(); }} />
        {!esEscalar && (
          <SelectorOrden nombre="B" matriz={B} onCambiar={(m) => { setB(m); limpiar(); }} />
        )}
        {!esEscalar && (
          <span className={`p3-dim ${mismoOrden ? "p3-dim-ok" : "p3-dim-mal"}`}>
            A <strong>{orden(A)}</strong> · B <strong>{orden(B)}</strong>
            {mismoOrden ? " → mismo orden ✓" : " → órdenes distintos ✗"}
          </span>
        )}
      </div>

      <div className="p3-lienzo">
        {esEscalar ? (
          <label className="flex items-center gap-2">
            <span className="font-display text-xl font-bold">c</span>
            <input
              type="text"
              value={c}
              aria-label="Escalar c"
              onChange={(evento) => {
                setC(evento.target.value);
                limpiar();
              }}
              className={
                "h-10 w-20 rounded-md border bg-superficie px-2 text-center font-mono " +
                (celdaConError(error, "c") !== null
                  ? "border-inconsistente ring-2 ring-inconsistente/40"
                  : "border-[var(--borde)] focus:border-pivote")
              }
            />
          </label>
        ) : (
          editor("A", A, setA)
        )}
        <Operador>{simbolo}</Operador>
        {esEscalar ? editor("A", A, setA) : editor("B", B, setB)}
        <Operador>=</Operador>
        <span className="font-display text-3xl text-grafito/50">?</span>
      </div>

      <Boton onClick={calcular} disabled={cargando}>
        {cargando ? "Calculando…" : "Calcular"}
      </Boton>

      {cargando && <Cargando />}
      <AvisoError error={error} />
      {resultado && <ResultadoMatrices resultado={resultado} simbolo={simbolo} />}
    </div>
  );
}

function ResultadoMatrices({ resultado, simbolo }) {
  const esEscalar = resultado.operacion === "escalar";
  const nombre = esEscalar
    ? `${resultado.c.fraccion}·A`
    : resultado.operacion === "suma"
      ? "A + B"
      : "A − B";

  return (
    <TarjetaResultado titulo="Resultado" formula={resultado.formula}>
      <div className="flex flex-wrap items-center gap-3 overflow-x-auto">
        {esEscalar ? (
          <span className="font-mono text-xl font-bold">{resultado.c.fraccion}</span>
        ) : (
          <BloqueMatriz nombre="" orden="A">
            <MatrizEstatica matriz={resultado.A} aumentada={false} />
          </BloqueMatriz>
        )}
        <Operador>{simbolo}</Operador>
        <BloqueMatriz nombre="" orden={esEscalar ? "A" : "B"}>
          <MatrizEstatica matriz={esEscalar ? resultado.A : resultado.B} aumentada={false} />
        </BloqueMatriz>
        <Operador>=</Operador>
        <BloqueMatriz nombre="" orden={nombre}>
          <div className="rounded-xl bg-determinado/10 p-1">
            <MatrizEstatica matriz={resultado.resultado} aumentada={false} />
          </div>
        </BloqueMatriz>
      </div>
      <p className="mt-4 text-sm text-grafito">
        Cada elemento se calcula posición a posición:{" "}
        <code>{resultado.formula}</code>.
      </p>
    </TarjetaResultado>
  );
}
