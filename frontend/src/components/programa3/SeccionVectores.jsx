// Opciones 1, 2 y 3 del Programa 3: u + v, u − v y c·v en ℝⁿ.

import { useState } from "react";
import { programa3 } from "../../lib/api.js";
import Boton from "../ui/Boton.jsx";
import SelectorDimension from "../ui/SelectorDimension.jsx";
import {
  AvisoError,
  Cargando,
  DIMENSION_MAXIMA,
  DIMENSION_MINIMA,
  EditorMatriz,
  Operador,
  SelectorOperacion,
  TarjetaResultado,
  VectorColumna,
  celdaConError,
  redimensionarVector,
  textoVector,
  useOperacion,
} from "./comunes.jsx";

const OPERACIONES = [
  { id: "suma", etiqueta: "u + v", simbolo: "+" },
  { id: "resta", etiqueta: "u − v", simbolo: "−" },
  { id: "escalar", etiqueta: "c · v", simbolo: "·" },
];

const CASOS = [
  { nombre: "Suma en ℝ³", operacion: "suma", u: ["1", "2", "3"], v: ["4", "5", "6"] },
  { nombre: "Resta en ℝ³", operacion: "resta", u: ["7", "4", "-3"], v: ["1", "-2", "-5"] },
  { nombre: "Escalar −1", operacion: "escalar", c: "-1", v: ["0", "1.5"] },
  { nombre: "Dimensiones distintas", operacion: "resta", u: ["1", "2"], v: ["1", "2", "3"] },
];

// Un vector ℝⁿ se edita como matriz columna n×1.
const aColumna = (vector) => vector.map((valor) => [valor]);

export default function SeccionVectores() {
  const [operacion, setOperacion] = useState("suma");
  const [u, setU] = useState(["", "", ""]);
  const [v, setV] = useState(["", "", ""]);
  const [c, setC] = useState("2");
  const { resultado, error, cargando, ejecutar, limpiar } = useOperacion();

  const esEscalar = operacion === "escalar";
  const simbolo = OPERACIONES.find((o) => o.id === operacion).simbolo;

  function cargarCaso(caso) {
    setOperacion(caso.operacion);
    if (caso.u) setU([...caso.u]);
    setV([...caso.v]);
    if (caso.c) setC(caso.c);
    limpiar();
  }

  function calcular() {
    ejecutar(() =>
      programa3.vectores({ operacion, u: esEscalar ? [] : u, v, c: esEscalar ? c : null })
    );
  }

  const editorVector = (nombre, valores, fijar) => (
    <div className="flex items-center gap-2">
      <span className="font-display text-xl font-bold">{nombre}</span>
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
    </div>
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

      <div className="flex flex-wrap gap-x-8 gap-y-3">
        {!esEscalar && (
          <SelectorDimension
            id="dim-u"
            etiqueta="Dimensión de u"
            valor={u.length}
            minimo={DIMENSION_MINIMA}
            maximo={DIMENSION_MAXIMA}
            onCambiar={(n) => {
              setU(redimensionarVector(u, n));
              limpiar();
            }}
          />
        )}
        <SelectorDimension
          id="dim-v"
          etiqueta="Dimensión de v"
          valor={v.length}
          minimo={DIMENSION_MINIMA}
          maximo={DIMENSION_MAXIMA}
          onCambiar={(n) => {
            setV(redimensionarVector(v, n));
            limpiar();
          }}
        />
      </div>

      <div className="p3-lienzo">
        {esEscalar ? (
          <label className="flex items-center gap-2">
            <span className="font-display text-xl font-bold">c</span>
            <input
              type="text"
              value={c}
              onChange={(evento) => {
                setC(evento.target.value);
                limpiar();
              }}
              aria-label="Escalar c"
              className={
                "h-10 w-20 rounded-md border bg-superficie px-2 text-center font-mono " +
                (celdaConError(error, "c") !== null
                  ? "border-inconsistente ring-2 ring-inconsistente/40"
                  : "border-[var(--borde)] focus:border-pivote")
              }
            />
          </label>
        ) : (
          editorVector("u", u, setU)
        )}
        <Operador>{simbolo}</Operador>
        {editorVector("v", v, setV)}
        <Operador>=</Operador>
        <span className="font-display text-3xl text-grafito/50">?</span>
      </div>

      <Boton onClick={calcular} disabled={cargando}>
        {cargando ? "Calculando…" : "Calcular"}
      </Boton>

      {cargando && <Cargando />}
      <AvisoError error={error} />
      {resultado && <ResultadoVectores resultado={resultado} simbolo={simbolo} />}
    </div>
  );
}

function ResultadoVectores({ resultado, simbolo }) {
  const esEscalar = resultado.operacion === "escalar";
  return (
    <TarjetaResultado titulo="Resultado" formula={resultado.formula}>
      <div className="flex flex-wrap items-center gap-3">
        {esEscalar ? (
          <span className="font-mono text-xl font-bold">{resultado.c.fraccion}</span>
        ) : (
          <VectorColumna vector={resultado.u} />
        )}
        <Operador>{simbolo}</Operador>
        <VectorColumna vector={resultado.v} />
        <Operador>=</Operador>
        <div className="rounded-xl bg-determinado/10 p-1">
          <VectorColumna vector={resultado.resultado} />
        </div>
      </div>

      <p className="mt-4 font-mono text-base font-semibold text-determinado">
        {esEscalar ? "c·v" : `u ${simbolo} v`} = {textoVector(resultado.resultado)}
      </p>

      <ol className="mt-4 grid gap-2 sm:grid-cols-2">
        {resultado.detalle.map((linea, i) => (
          <li key={i} className="math-equation-line font-mono text-sm">
            <span className="text-grafito">componente {i + 1}: </span>
            {linea}
          </li>
        ))}
      </ol>
    </TarjetaResultado>
  );
}
