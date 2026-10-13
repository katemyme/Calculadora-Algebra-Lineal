// Opciones 7 y 8 del Programa 5: A⁻¹ por Gauss-Jordan sobre [A | I] o por la
// matriz adjunta. Con cualquiera de los dos métodos el backend comprueba
// después que A·A⁻¹ = I y devuelve el diagnóstico de invertibilidad.
//
// La adjunta se muestra paso a paso: det(A), el menor y el cofactor de cada
// elemento, la matriz de cofactores C, adj(A) = Cᵀ y A⁻¹ = (1/det A)·adj(A).

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
import { MenorDeEntrada, SumaDeTerminos } from "./MenoresYCofactores.jsx";
import {
  BotonesDeCasos,
  Diagnostico,
  EditorNombrado,
  FlechaDePaso,
  ListaDeOperaciones,
  MatrizNombrada,
  PlanDePasos,
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
        <EditorNombrado nombre="A" matriz={A} onCambiar={fijarA} error={error} soloCuadrada />
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

const ETAPAS_ADJUNTA = [
  "Calcular det(A) y ver si es ≠ 0",
  "Menor y cofactor de cada elemento",
  "Armar la matriz de cofactores C",
  "Transponer: adj(A) = Cᵀ",
  "Dividir entre det(A) y comprobar",
];

// Hasta este orden los menores de todas las filas se muestran abiertos; con matrices
// mayores ocupan mucho y cada fila se abre a petición.
const ORDEN_MAXIMO_DESPLEGADO = 3;

function ResultadoAdjunta({ resultado }) {
  const { inversa } = resultado;
  const determinante = textoFraccion(resultado.determinante);

  return (
    <TarjetaResultado titulo="Inversa por matriz adjunta" formula="A⁻¹ = (1/det A)·adj(A)">
      <div className="space-y-5">
        <PlanDePasos etapas={ETAPAS_ADJUNTA} />
        <DeterminanteYDecision resultado={resultado} />
        <MenoresDeCadaElemento resultado={resultado} />

        <TarjetaNumerada numero="3" titulo="Armar la matriz de cofactores C">
          <div className="flex overflow-x-auto">
            <MatrizNombrada nombre="C" matriz={resultado.cofactores} />
          </div>
          <p className="text-sm text-grafito">
            Cada cofactor Cᵢⱼ = (−1)ⁱ⁺ʲ·det(Mᵢⱼ) del paso 2 ocupa la fila i y la columna j.
          </p>
        </TarjetaNumerada>

        <TarjetaNumerada numero="4" titulo="Transponer: la matriz adjunta" nota="adj(A) = Cᵀ">
          <div className="flex flex-wrap items-center gap-x-4 gap-y-3 overflow-x-auto">
            <MatrizNombrada nombre="C" matriz={resultado.cofactores} />
            <FlechaDePaso>las filas pasan a ser columnas</FlechaDePaso>
            <MatrizNombrada nombre="adj(A)" matriz={resultado.adjunta} copiable />
          </div>
        </TarjetaNumerada>

        {inversa ? (
          <InversaComprobada
            numero="5"
            titulo="Dividir la adjunta entre det(A) y comprobar"
            resultado={resultado}
          >
            <p className="lu-ecuacion">
              A⁻¹ = (1/det A)·adj(A) = (1/({determinante}))·adj(A)
            </p>
          </InversaComprobada>
        ) : (
          <p className="math-note">
            El método se detiene aquí: el paso 5 pediría dividir adj(A) entre det(A) = 0.
          </p>
        )}
        <Diagnostico diagnostico={resultado.diagnostico} />
      </div>
    </TarjetaResultado>
  );
}

/** Paso 1: det(A) por la fila 1 y si la matriz tiene inversa. */
function DeterminanteYDecision({ resultado }) {
  const { inversa, n } = resultado;
  const { terminos } = resultado.expansion_determinante;
  const determinante = textoFraccion(resultado.determinante);

  return (
    <TarjetaNumerada numero="1" titulo="Calcular det(A)" nota={`det(A) = ${determinante}`}>
      <p className="lu-ecuacion">
        det(A) ={" "}
        {n > 1 && (
          <>
            <SumaDeTerminos terminos={terminos} /> ={" "}
          </>
        )}
        <span className="font-semibold text-tinta">{determinante}</span>
      </p>
      <p className="text-sm text-grafito">
        {n > 1
          ? "Se desarrolla por la fila 1: cada entrada a₁ⱼ por su cofactor C₁ⱼ, que se " +
            "calcula en el paso 2. El desarrollo completo está en las pestañas «Cofactores» " +
            "y «Regla de Sarrus»."
          : "El determinante de una matriz 1×1 es su único elemento."}
      </p>
      <Veredicto cumple={Boolean(inversa)}>
        {inversa
          ? `det(A) = ${determinante} ≠ 0: A tiene inversa`
          : "det(A) = 0: A no tiene inversa"}
      </Veredicto>
      {!inversa && (
        <p className="text-sm text-tinta">
          La fórmula A⁻¹ = (1/det A)·adj(A) pediría dividir entre 0. Que det(A) = 0 significa
          que las filas de A son linealmente dependientes: A no llega a tener {n} pivotes y
          ninguna matriz B cumple A·B = I.
        </p>
      )}
    </TarjetaNumerada>
  );
}

/** Paso 2: el menor y el cofactor de cada elemento de A, agrupados por fila. */
function MenoresDeCadaElemento({ resultado }) {
  const { A, n, menores, nota_menores: nota } = resultado;

  return (
    <TarjetaNumerada
      numero="2"
      titulo="Calcular el menor y el cofactor de cada elemento"
      nota={menores ? `${n * n} menores, uno por elemento` : undefined}
    >
      {menores && (
        <p className="text-sm text-grafito">
          Para el elemento aᵢⱼ se tachan la fila i y la columna j de A (en azul): lo que queda
          es el menor Mᵢⱼ. Su determinante, con el signo (−1)ⁱ⁺ʲ, es el cofactor Cᵢⱼ.
        </p>
      )}
      {menores?.map((terminos, fila) => (
        <MenoresDeFila
          key={fila}
          A={A}
          terminos={terminos}
          fila={fila}
          abierto={n <= ORDEN_MAXIMO_DESPLEGADO}
        />
      ))}
      {nota && <p className="math-note">{nota}</p>}
    </TarjetaNumerada>
  );
}

/** Los menores de los elementos de una fila; `abierto` fija cómo empieza el bloque. */
function MenoresDeFila({ A, terminos, fila, abierto }) {
  const [visible, setVisible] = useState(abierto);
  const cofactores = terminos
    .map((termino) => `${termino.nombre_cofactor} = ${textoFraccion(termino.cofactor)}`)
    .join(",  ");

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-3">
        <p className="font-display text-sm font-bold text-tinta">Fila {fila + 1}</p>
        <span className="font-mono text-xs text-grafito">{cofactores}</span>
        <Boton
          variante="secundario"
          className="text-xs"
          aria-expanded={visible}
          onClick={() => setVisible((previo) => !previo)}
        >
          {visible ? "Ocultar los menores" : "Ver los menores de esta fila"}
        </Boton>
      </div>
      {visible && (
        <ol className="space-y-4" style={{ animation: "aparecer-paso 0.3s ease both" }}>
          {terminos.map((termino) => (
            <MenorDeEntrada key={termino.columna} A={A} termino={termino} />
          ))}
        </ol>
      )}
    </div>
  );
}

/** A⁻¹ y la comprobación A·A⁻¹ = I que hizo el backend con su propio producto. */
function InversaComprobada({ numero, resultado, titulo = "Inversa y comprobación", children }) {
  const { A, inversa, comprobacion } = resultado;
  const esIdentidad = comprobacion.es_identidad;

  return (
    <TarjetaNumerada numero={numero} titulo={titulo}>
      {children}
      <div className="flex flex-wrap items-center gap-3 overflow-x-auto">
        <span className="font-display text-lg font-bold text-tinta">A⁻¹ =</span>
        <MatrizNombrada nombre="A⁻¹" matriz={inversa} destacada copiable />
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
