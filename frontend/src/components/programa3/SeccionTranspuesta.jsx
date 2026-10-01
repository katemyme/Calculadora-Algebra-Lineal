// Matrices → Transpuesta: demostración de los cuatro teoremas de la matriz
// transpuesta. Cada botón pide al backend ("backend/calculo/transpuesta.py")
// el desarrollo y la comparación elemento por elemento; aquí solo se
// presentan esos datos (fórmulas con KaTeX y la transposición animada).
//  - (Aᵀ)ᵀ = A: una sola matriz, cadena A → Aᵀ → (Aᵀ)ᵀ.
//  - Los otros tres: lado izquierdo y lado derecho.

import { useState } from "react";
import { ErrorDeCalculo, programa3 } from "../../lib/api.js";
import Boton from "../ui/Boton.jsx";
import SelectorDimension from "../ui/SelectorDimension.jsx";
import Tex, { TextoTex } from "../Tex.jsx";
import VisualEscalar from "./VisualEscalar.jsx";
import VisualProducto from "./VisualProducto.jsx";
import VisualSuma from "./VisualSuma.jsx";
import VisualTranspuesta, { MatrizColor } from "./VisualTranspuesta.jsx";
import {
  AvisoError,
  BloqueMatriz,
  Cargando,
  DIMENSION_MAXIMA,
  DIMENSION_MINIMA,
  EditorMatriz,
  Operador,
  TarjetaResultado,
  cambiarCelda,
  celdaConError,
  redimensionarRejilla,
  useOperacion,
} from "./comunes.jsx";

const TEOREMAS = [
  { id: "doble", tex: "(A^{T})^{T} = A" },
  { id: "suma", tex: "(A + B)^{T} = A^{T} + B^{T}" },
  { id: "escalar", tex: "(rA)^{T} = r\\,A^{T}" },
  { id: "producto", tex: "(AB)^{T} = B^{T}A^{T}" },
];

const CASOS = [
  {
    nombre: "A 2×3, B 3×2",
    A: [["1", "2", "3"], ["4", "5", "6"]],
    B: [["7", "8"], ["9", "10"], ["11", "12"]],
    r: "3",
  },
  {
    nombre: "A y B 2×2",
    A: [["2", "-1"], ["0", "1/2"]],
    B: [["1", "4"], ["-3", "5"]],
    r: "-2",
  },
];

/** Filas y columnas de una matriz (ids propios para no chocar con otras secciones). */
function SelectorOrdenTranspuesta({ nombre, matriz, onCambiar }) {
  return (
    <div className="flex flex-wrap items-center gap-x-5 gap-y-2">
      <span className="font-display text-sm font-bold">{nombre}</span>
      <SelectorDimension
        id={`transpuesta-filas-${nombre}`}
        etiqueta="filas"
        valor={matriz.length}
        minimo={DIMENSION_MINIMA}
        maximo={DIMENSION_MAXIMA}
        onCambiar={(filas) => onCambiar(redimensionarRejilla(matriz, filas, matriz[0].length))}
      />
      <SelectorDimension
        id={`transpuesta-columnas-${nombre}`}
        etiqueta="columnas"
        valor={matriz[0].length}
        minimo={DIMENSION_MINIMA}
        maximo={DIMENSION_MAXIMA}
        onCambiar={(columnas) => onCambiar(redimensionarRejilla(matriz, matriz.length, columnas))}
      />
    </div>
  );
}

export default function SeccionTranspuesta() {
  const [A, setA] = useState(CASOS[0].A.map((f) => [...f]));
  const [B, setB] = useState(CASOS[0].B.map((f) => [...f]));
  const [r, setR] = useState(CASOS[0].r);
  const [teorema, setTeorema] = useState(null);
  const { resultado, error, cargando, ejecutar, limpiar } = useOperacion();

  function cambiar(fijar) {
    return (valor) => {
      fijar(valor);
      limpiar();
    };
  }

  function cargarCaso(caso) {
    setA(caso.A.map((f) => [...f]));
    setB(caso.B.map((f) => [...f]));
    setR(caso.r);
    limpiar();
  }

  function limpiarTodo() {
    setA(redimensionarRejilla([], A.length, A[0].length));
    setB(redimensionarRejilla([], B.length, B[0].length));
    setR("");
    limpiar();
  }

  function demostrar(id) {
    setTeorema(id);
    ejecutar(() => programa3.transpuesta({ teorema: id, A, B, r }));
  }

  const errorEnR = error instanceof ErrorDeCalculo && error.campo === "r";

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap gap-2">
        {CASOS.map((caso) => (
          <Boton key={caso.nombre} variante="secundario" className="text-xs" onClick={() => cargarCaso(caso)}>
            {caso.nombre}
          </Boton>
        ))}
        <Boton variante="fantasma" className="text-xs" onClick={limpiarTodo}>
          Limpiar
        </Boton>
      </div>

      <div className="space-y-3">
        <SelectorOrdenTranspuesta nombre="A" matriz={A} onCambiar={cambiar(setA)} />
        <SelectorOrdenTranspuesta nombre="B" matriz={B} onCambiar={cambiar(setB)} />
      </div>

      <div className="p3-lienzo">
        {[["A", A, setA], ["B", B, setB]].map(([nombre, matriz, fijar]) => (
          <BloqueMatriz key={nombre} nombre={nombre} orden={`${matriz.length}×${matriz[0].length}`}>
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
        ))}

        <label className="flex items-center gap-2">
          <Tex tex="r =" className="text-lg text-tinta" />
          <input
            type="text"
            autoComplete="off"
            spellCheck={false}
            placeholder="escalar"
            aria-label="Escalar r"
            aria-invalid={errorEnR || undefined}
            value={r}
            onChange={(evento) => {
              setR(evento.target.value);
              limpiar();
            }}
            className={
              "h-9 w-24 rounded-md border bg-superficie px-2 text-center font-mono text-sm " +
              (errorEnR
                ? "border-inconsistente ring-2 ring-inconsistente/40"
                : "border-[var(--borde)] focus:border-pivote")
            }
          />
        </label>
      </div>

      <div className="flex flex-wrap gap-2">
        {TEOREMAS.map((t) => (
          <Boton
            key={t.id}
            variante={t.id === teorema && (resultado || cargando) ? "primario" : "secundario"}
            onClick={() => demostrar(t.id)}
            disabled={cargando}
          >
            <Tex tex={t.tex} />
          </Boton>
        ))}
      </div>

      {cargando && <Cargando texto="Desarrollando el teorema…" />}
      <AvisoError error={error} />
      {resultado && <ResultadoTranspuesta resultado={resultado} />}
    </div>
  );
}

function ResultadoTranspuesta({ resultado }) {
  return (
    <TarjetaResultado
      titulo={
        <>
          Teorema: <Tex tex={resultado.enunciado} />
        </>
      }
    >
      <div className="space-y-8">
        {resultado.modo === "cadena" ? (
          <Cadena resultado={resultado} />
        ) : (
          <>
            <Lado titulo="Lado izquierdo" tex={resultado.comparacion.nombre_izquierda} pasos={resultado.izquierda} />
            <Lado titulo="Lado derecho" tex={resultado.comparacion.nombre_derecha} pasos={resultado.derecha} />
          </>
        )}
        <Comparacion comparacion={resultado.comparacion} razonamiento={resultado.razonamiento} />
      </div>
    </TarjetaResultado>
  );
}

/** (Aᵀ)ᵀ = A: una sola matriz que se transpone dos veces. */
function Cadena({ resultado }) {
  return <FilaDePasos pasos={resultado.pasos} />;
}

/** Los pasos uno al lado del otro; si no caben, la fila se desplaza en horizontal. */
function FilaDePasos({ pasos }) {
  return (
    <div className="flex items-start gap-4 overflow-x-auto pb-2">
      {pasos.map((paso, indice) => (
        <Paso key={indice} numero={indice + 1} paso={paso} />
      ))}
    </div>
  );
}

function Lado({ titulo, tex, pasos }) {
  return (
    <div className="min-w-0 space-y-4">
      <p className="font-display text-base font-bold text-pivote">
        {titulo}: <Tex tex={tex} />
      </p>
      <FilaDePasos pasos={pasos} />
    </div>
  );
}

function Paso({ numero, paso }) {
  return (
    <div className="math-info-card w-max min-w-[16rem] shrink-0 space-y-3">
      <p className="w-0 min-w-full text-sm text-tinta">
        <span className="font-semibold">Paso {numero}.</span> <TextoTex texto={paso.descripcion} />
      </p>

      {paso.escalar_de ? (
        <VisualEscalar
          escalar={paso.escalar_de}
          resultado={{ nombre: paso.nombre, matriz: paso.matriz }}
        />
      ) : paso.producto_de ? (
        <VisualProducto
          factores={paso.producto_de}
          resultado={{ nombre: paso.nombre, matriz: paso.matriz }}
        />
      ) : paso.suma_de ? (
        <VisualSuma
          sumandos={paso.suma_de}
          resultado={{ nombre: paso.nombre, matriz: paso.matriz }}
        />
      ) : paso.transpuesta_de ? (
        <VisualTranspuesta
          origen={paso.transpuesta_de}
          destino={{ nombre: paso.nombre, matriz: paso.matriz }}
        />
      ) : (
        <div className="flex items-center gap-2 overflow-x-auto">
          <Tex tex={`${paso.nombre} =`} className="text-lg" />
          <MatrizColor matriz={paso.matriz} />
          <span className="text-xs text-grafito">{paso.orden}</span>
        </div>
      )}

      {paso.detalle.length > 0 && (
        <details className="w-0 min-w-full">
          <summary className="cursor-pointer text-xs font-semibold text-grafito">
            Cálculo entrada por entrada ({paso.detalle.length})
          </summary>
          <div className="mt-2 space-y-1 overflow-x-auto text-sm text-tinta">
            {paso.detalle.map((linea, i) => (
              <Tex key={i} tex={linea} bloque className="[&_.katex-display]:my-1 [&_.katex-display]:text-left" />
            ))}
          </div>
        </details>
      )}
    </div>
  );
}

function Comparacion({ comparacion, razonamiento }) {
  const {
    nombre_izquierda: izq,
    nombre_derecha: der,
    izquierda,
    derecha,
    orden_izquierda: ordenIzq,
    orden_derecha: ordenDer,
    iguales,
    cumple,
  } = comparacion;

  const estilo = (i, j) => {
    if (iguales.length === 0) return null;
    const color = iguales[i][j] ? "#0e9f6e" : "#d63c4a";
    return { color };
  };

  return (
    <div className="space-y-4">
      <p className="font-display text-base font-bold text-pivote">
        Comparación elemento por elemento
      </p>

      <div className="flex flex-wrap items-center gap-3 overflow-x-auto">
        <Tex tex={izq} className="text-lg" />
        <MatrizColor matriz={izquierda} estiloCelda={estilo} />
        <Operador>{cumple ? "=" : "≠"}</Operador>
        <MatrizColor matriz={derecha} estiloCelda={estilo} />
        <Tex tex={der} className="text-lg" />
      </div>

      {iguales.length === 0 ? (
        <p className="text-sm text-inconsistente">
          <Tex tex={izq} /> es {ordenIzq} y <Tex tex={der} /> es {ordenDer}: tienen órdenes
          distintos, no pueden ser iguales.
        </p>
      ) : (
        <p className="text-sm text-grafito">
          En verde, las entradas que coinciden en la misma posición.
        </p>
      )}

      {razonamiento?.length > 0 && (
        <div className="rounded-lg border border-[var(--borde)] bg-white px-4 py-2">
          <p className="text-xs font-semibold text-grafito">¿Por qué siempre se cumple?</p>
          {razonamiento.map((linea, i) => (
            <Tex key={i} tex={linea} bloque />
          ))}
          <p className="text-xs text-grafito">
            Transponer dos veces intercambia los índices dos veces, así que cada entrada vuelve a su
            lugar.
          </p>
        </div>
      )}

      <div className={`math-solution-banner ${cumple ? "math-solution-ok" : "math-solution-error"}`}>
        <div
          className="math-solution-icon"
          style={{ color: `var(--${cumple ? "determinado" : "inconsistente"})` }}
        >
          {cumple ? "=" : "≠"}
        </div>
        <div>
          <p className={`text-lg font-bold ${cumple ? "text-determinado" : "text-inconsistente"}`}>
            <Tex tex={`${izq} ${cumple ? "=" : "\\neq"} ${der}`} />
          </p>
          <p className="mt-1 text-sm text-tinta">
            {cumple
              ? `Ambas matrices son ${ordenIzq} y coinciden en todas sus entradas, como afirma el teorema.`
              : "Las matrices no coinciden."}
          </p>
        </div>
      </div>
    </div>
  );
}
