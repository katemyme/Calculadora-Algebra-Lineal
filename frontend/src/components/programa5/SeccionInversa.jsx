// Opciones 7 y 8 del Programa 5: A⁻¹ por Gauss-Jordan sobre [A | I] o por la
// matriz adjunta. Con cualquiera de los dos métodos el backend comprueba
// después que A·A⁻¹ = I y devuelve el diagnóstico de invertibilidad.

import { useState } from "react";
import { programa5 } from "../../lib/api.js";
import { textoFraccion } from "../../lib/formato.js";
import Boton from "../ui/Boton.jsx";
import MatrizEstatica from "../MatrizEstatica.jsx";
import ReduccionPorFilas from "../programa4/ReduccionPorFilas.jsx";
import {
  AvisoError,
  BloqueMatriz,
  Cargando,
  Operador,
  SelectorOperacion,
  TarjetaResultado,
  redimensionarRejilla,
  useOperacion,
} from "../programa3/comunes.jsx";
import {
  BotonesDeCasos,
  Diagnostico,
  EditorNombrado,
  ListaDeOperaciones,
  MatrizNombrada,
  SelectorOrdenN,
  TarjetaNumerada,
  Veredicto,
  copiarRejilla,
} from "./comunes.jsx";

const METODOS = [
  {
    id: "gauss_jordan",
    etiqueta: "Gauss-Jordan [A | I]",
    pistas: ["[A | I] → [I | A⁻¹]", "n pivotes ⇔ A invertible", "menos de n pivotes ⇒ singular"],
  },
  {
    id: "adjunta",
    etiqueta: "Matriz adjunta",
    pistas: ["adj(A) = Cᵀ", "A⁻¹ = (1/det A)·adj(A)", "solo si det(A) ≠ 0"],
  },
];

const CASOS = [
  { nombre: "Invertible 3×3", A: [["1", "2", "3"], ["0", "1", "4"], ["5", "6", "0"]] },
  { nombre: "Invertible 2×2", A: [["1", "2"], ["3", "4"]] },
  { nombre: "Singular 3×3", A: [["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"]] },
];

export default function SeccionInversa() {
  const [metodo, setMetodo] = useState("gauss_jordan");
  const [A, setA] = useState(() => copiarRejilla(CASOS[0].A));
  const { resultado, error, cargando, ejecutar, limpiar } = useOperacion();
  const n = A.length;
  const definicion = METODOS.find((opcion) => opcion.id === metodo);

  function fijarA(nueva) {
    setA(nueva);
    limpiar();
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <SelectorOperacion
          opciones={METODOS}
          activa={metodo}
          onCambiar={(id) => {
            setMetodo(id);
            limpiar();
          }}
        />
        <BotonesDeCasos
          casos={CASOS}
          onCargar={(caso) => fijarA(copiarRejilla(caso.A))}
          onLimpiar={() => fijarA(redimensionarRejilla([], n, n))}
        />
      </div>

      <SelectorOrdenN
        id="p5-inversa-n"
        valor={n}
        onCambiar={(orden) => fijarA(redimensionarRejilla(A, orden, orden))}
      />

      <div className="math-formula-strip" aria-hidden="true">
        {definicion.pistas.map((pista) => (
          <span key={pista}>{pista}</span>
        ))}
      </div>

      <div className="p3-lienzo">
        <EditorNombrado nombre="A" matriz={A} onCambiar={fijarA} error={error} />
        <Operador>⁻¹</Operador>
        <Operador>=</Operador>
        <span className="font-display text-3xl text-grafito/50">?</span>
      </div>

      <Boton onClick={() => ejecutar(() => programa5.inversa({ metodo, A }))} disabled={cargando}>
        {cargando ? "Calculando…" : "Calcular A⁻¹"}
      </Boton>

      {cargando && <Cargando texto="Calculando la inversa…" />}
      <AvisoError error={error} />
      {resultado?.metodo === "gauss_jordan" && <ResultadoGaussJordan resultado={resultado} />}
      {resultado?.metodo === "adjunta" && <ResultadoAdjunta resultado={resultado} />}
    </div>
  );
}

function ResultadoGaussJordan({ resultado }) {
  const [verPasoAPaso, setVerPasoAPaso] = useState(false);
  const { n, inversa, pivotes, columnas_pivote: columnasPivote } = resultado;
  const orden = `${n} × ${n + n}`;

  return (
    <TarjetaResultado titulo="Inversa por Gauss-Jordan" formula="[A | I] → [I | A⁻¹]">
      <div className="space-y-5">
        <TarjetaNumerada numero="1" titulo="Matriz aumentada [A | I]">
          <div className="flex overflow-x-auto">
            <BloqueMatriz orden={orden}>
              <MatrizEstatica matriz={resultado.aumentada_inicial} columnasDerecha={n} />
            </BloqueMatriz>
          </div>
        </TarjetaNumerada>

        <TarjetaNumerada
          numero="2"
          titulo="Operaciones elementales de fila"
          nota={`${resultado.pasos.length} operaciones`}
        >
          <ListaDeOperaciones operaciones={resultado.pasos} />
          {resultado.pasos.length > 0 && (
            <Boton
              variante="secundario"
              aria-expanded={verPasoAPaso}
              onClick={() => setVerPasoAPaso((previo) => !previo)}
            >
              {verPasoAPaso ? "Ocultar el paso a paso" : "Ver el paso a paso"}
            </Boton>
          )}
          {verPasoAPaso && (
            <div style={{ animation: "aparecer-paso 0.3s ease both" }}>
              <ReduccionPorFilas
                matrizInicial={resultado.aumentada_inicial}
                pasos={resultado.pasos_detalle}
                columnasPivote={columnasPivote}
                columnasDerecha={n}
              />
            </div>
          )}
        </TarjetaNumerada>

        <TarjetaNumerada
          numero="3"
          titulo={inversa ? "Matriz final [I | A⁻¹]" : "Reducción detenida antes de I"}
          nota={`${pivotes} de ${n} posiciones pivote`}
        >
          <div className="flex overflow-x-auto">
            <BloqueMatriz orden={orden}>
              <MatrizEstatica
                matriz={resultado.aumentada_final}
                columnasDerecha={n}
                columnasPivote={columnasPivote}
              />
            </BloqueMatriz>
          </div>
          {!inversa && (
            <p className="math-note">
              Sin {n} pivotes el bloque izquierdo no llega a ser I: la matriz es singular y
              no se calcula ninguna inversa.
            </p>
          )}
        </TarjetaNumerada>

        {inversa && <InversaComprobada numero="4" resultado={resultado} />}
        <Diagnostico diagnostico={resultado.diagnostico} />
      </div>
    </TarjetaResultado>
  );
}

function ResultadoAdjunta({ resultado }) {
  const { inversa } = resultado;
  const determinante = textoFraccion(resultado.determinante);

  return (
    <TarjetaResultado titulo="Inversa por matriz adjunta" formula="A⁻¹ = (1/det A)·adj(A)">
      <div className="space-y-5">
        <TarjetaNumerada numero="1" titulo="Matriz de cofactores y adjunta" nota="adj(A) = Cᵀ">
          <div className="flex flex-wrap items-center gap-3 overflow-x-auto">
            <MatrizNombrada nombre="C" matriz={resultado.cofactores} />
            <Operador>ᵀ</Operador>
            <Operador>=</Operador>
            <MatrizNombrada nombre="adj(A)" matriz={resultado.adjunta} />
          </div>
          <p className="text-sm text-grafito">
            Cada cofactor es Cᵢⱼ = (−1)ⁱ⁺ʲ·det(Mᵢⱼ); la adjunta es la transpuesta de C.
          </p>
        </TarjetaNumerada>

        <TarjetaNumerada numero="2" titulo="Determinante" nota={`det(A) = ${determinante}`}>
          <p className="font-mono text-sm">
            {inversa
              ? `det(A) = ${determinante} ≠ 0  ⇒  A⁻¹ = (1/(${determinante}))·adj(A)`
              : "det(A) = 0: no se puede dividir entre det(A), así que no existe A⁻¹."}
          </p>
        </TarjetaNumerada>

        {inversa && <InversaComprobada numero="3" resultado={resultado} />}
        <Diagnostico diagnostico={resultado.diagnostico} />
      </div>
    </TarjetaResultado>
  );
}

/** A⁻¹ y la comprobación A·A⁻¹ = I que hizo el backend con su propio producto. */
function InversaComprobada({ numero, resultado }) {
  const { A, inversa, comprobacion } = resultado;
  const esIdentidad = comprobacion.es_identidad;

  return (
    <TarjetaNumerada numero={numero} titulo="Inversa y comprobación">
      <div className="flex flex-wrap items-center gap-3 overflow-x-auto">
        <span className="font-display text-lg font-bold text-tinta">A⁻¹ =</span>
        <MatrizNombrada nombre="A⁻¹" matriz={inversa} destacada />
      </div>
      <div className="flex flex-wrap items-center gap-3 overflow-x-auto">
        <MatrizNombrada nombre="A" matriz={A} />
        <Operador>·</Operador>
        <MatrizNombrada nombre="A⁻¹" matriz={inversa} />
        <Operador>=</Operador>
        <MatrizNombrada nombre="A·A⁻¹" matriz={comprobacion.producto} />
      </div>
      <Veredicto cumple={esIdentidad}>
        {esIdentidad ? "A·A⁻¹ = I (igualdad exacta con fracciones)" : "A·A⁻¹ ≠ I"}
      </Veredicto>
    </TarjetaNumerada>
  );
}
