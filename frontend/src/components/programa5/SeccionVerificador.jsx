// Opción 9 del Programa 5: verificador de propiedades con A y B invertibles
// del mismo orden n.
//
//   1. (A⁻¹)⁻¹ = A            4. det(A⁻¹) = 1/det(A)
//   2. (AB)⁻¹ = B⁻¹A⁻¹        5. efecto de las operaciones de fila sobre det(A)
//   3. (Aᵀ)⁻¹ = (A⁻¹)ᵀ        6. matriz triangular: det = ± producto de la diagonal
//                             7. det(AB) = det(A)·det(B)
//
// El backend calcula ambos miembros de cada propiedad y decide el veredicto.
// También arma el paso a paso de cada cálculo ("procedimientos"); aquí solo se dibuja.

import { useState } from "react";
import { ErrorDeCalculo, programa5 } from "../../lib/api.js";
import { subindice, textoFraccion } from "../../lib/formato.js";
import Boton from "../ui/Boton.jsx";
import SelectorDimension from "../ui/SelectorDimension.jsx";
import { celdasCambiadas } from "../MatrizEstatica.jsx";
import VisualProducto from "../programa3/VisualProducto.jsx";
import VisualTranspuesta from "../programa3/VisualTranspuesta.jsx";
import ReduccionPorFilas from "../programa4/ReduccionPorFilas.jsx";
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
  CampoTexto,
  EditorNombrado,
  IgualdadEscalar,
  MatrizNombrada,
  ReduccionTriangular,
  SelectorOrdenN,
  TarjetaNumerada,
  Veredicto,
  copiarRejilla,
} from "./comunes.jsx";

const CASOS = [
  {
    nombre: "Caso 2×2",
    A: [["1", "2"], ["3", "4"]],
    B: [["0", "1"], ["1", "1"]],
    filas: {
      intercambio: { fila_i: 1, fila_j: 2 },
      reemplazo: { fila_i: 2, fila_j: 1, k: "-3" },
      escalamiento: { fila_i: 1, k: "3" },
    },
  },
  {
    nombre: "Caso 3×3 (propiedad 6)",
    A: [["1", "2", "3"], ["0", "1", "4"], ["5", "6", "0"]],
    B: [["1", "0", "0"], ["0", "2", "0"], ["0", "0", "3"]],
    filas: {
      intercambio: { fila_i: 1, fila_j: 3 },
      reemplazo: { fila_i: 3, fila_j: 1, k: "1/2" },
      escalamiento: { fila_i: 2, k: "-2" },
    },
  },
  {
    nombre: "B singular (error)",
    A: [["1", "2"], ["3", "4"]],
    B: [["1", "2"], ["2", "4"]],
    filas: {
      intercambio: { fila_i: 1, fila_j: 2 },
      reemplazo: { fila_i: 2, fila_j: 1, k: "-3" },
      escalamiento: { fila_i: 1, k: "3" },
    },
  },
];

export default function SeccionVerificador() {
  const [A, setA] = useState(() => copiarRejilla(CASOS[0].A));
  const [B, setB] = useState(() => copiarRejilla(CASOS[0].B));
  const [filas, setFilas] = useState(CASOS[0].filas);
  const { resultado, error, cargando, ejecutar, limpiar } = useOperacion();
  const n = A.length;

  // Envuelve un setter para descartar el resultado anterior al cambiar un dato.
  const alCambiar = (fijar) => (valor) => {
    fijar(valor);
    limpiar();
  };

  function cambiarOrden(orden) {
    setA(redimensionarRejilla(A, orden, orden));
    setB(redimensionarRejilla(B, orden, orden));
    limpiar();
  }

  function cargarCaso(caso) {
    setA(copiarRejilla(caso.A));
    setB(copiarRejilla(caso.B));
    setFilas(caso.filas);
    limpiar();
  }

  function cambiarFila(operacion, campo, valor) {
    setFilas((previas) => ({
      ...previas,
      [operacion]: { ...previas[operacion], [campo]: valor },
    }));
    limpiar();
  }

  // Una fila elegida con un orden mayor puede quedar fuera al reducir n.
  const dentro = (fila) => Math.min(fila, n);
  const { intercambio, reemplazo, escalamiento } = filas;

  function verificar() {
    const hayDosFilas = n >= 2;
    ejecutar(() =>
      programa5.verificador({
        A,
        B,
        intercambio: hayDosFilas
          ? { fila_i: dentro(intercambio.fila_i), fila_j: dentro(intercambio.fila_j) }
          : null,
        reemplazo: hayDosFilas
          ? { fila_i: dentro(reemplazo.fila_i), fila_j: dentro(reemplazo.fila_j), k: reemplazo.k }
          : null,
        escalamiento: { fila_i: dentro(escalamiento.fila_i), k: escalamiento.k },
      })
    );
  }

  const campoConError = error instanceof ErrorDeCalculo ? error.campo : null;
  const selectorDeFila = (operacion, campo, etiqueta) => (
    <SelectorDimension
      id={`p5-${operacion}-${campo}`}
      etiqueta={etiqueta}
      valor={dentro(filas[operacion][campo])}
      minimo={1}
      maximo={n}
      onCambiar={(valor) => cambiarFila(operacion, campo, valor)}
    />
  );
  const campoDeFactor = (operacion, descripcion) => (
    <CampoTexto
      etiqueta="k"
      descripcion={descripcion}
      valor={filas[operacion].k}
      onCambiar={(valor) => cambiarFila(operacion, "k", valor)}
      conError={campoConError === operacion}
    />
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <SelectorOrdenN id="p5-verificador-n" etiqueta="Orden n de A y B" valor={n} onCambiar={cambiarOrden} />
        <BotonesDeCasos
          casos={CASOS}
          onCargar={cargarCaso}
          onLimpiar={() => {
            setA(redimensionarRejilla([], n, n));
            setB(redimensionarRejilla([], n, n));
            limpiar();
          }}
        />
      </div>

      <div className="p3-lienzo">
        <EditorNombrado nombre="A" matriz={A} onCambiar={alCambiar(setA)} error={error} />
        <EditorNombrado nombre="B" matriz={B} onCambiar={alCambiar(setB)} error={error} />
        <p className="max-w-xs text-xs text-grafito">
          A y B deben ser <strong>cuadradas e invertibles</strong> del mismo orden. Si alguna
          es singular, el backend lo indica y no verifica nada.
        </p>
      </div>

      <div className="space-y-2">
        <p className="font-display text-sm font-bold text-tinta">
          Operaciones de fila para la propiedad 5 (se aplican a A)
        </p>
        {n >= 2 ? (
          <>
            <GrupoDeFila titulo="Intercambio" notacion="Fᵢ ↔ Fⱼ" conError={campoConError === "intercambio"}>
              {selectorDeFila("intercambio", "fila_i", "Fila i")}
              {selectorDeFila("intercambio", "fila_j", "Fila j")}
            </GrupoDeFila>
            <GrupoDeFila titulo="Reemplazo" notacion="Fᵢ → Fᵢ + k·Fⱼ" conError={campoConError === "reemplazo"}>
              {selectorDeFila("reemplazo", "fila_i", "Fila i")}
              {selectorDeFila("reemplazo", "fila_j", "Fila j")}
              {campoDeFactor("reemplazo", "Factor k del reemplazo")}
            </GrupoDeFila>
          </>
        ) : (
          <p className="math-note">
            Con n = 1 no hay dos filas distintas: se omiten el intercambio y el reemplazo.
          </p>
        )}
        <GrupoDeFila titulo="Escalamiento" notacion="Fᵢ → k·Fᵢ, con k ≠ 0" conError={campoConError === "escalamiento"}>
          {selectorDeFila("escalamiento", "fila_i", "Fila i")}
          {campoDeFactor("escalamiento", "Factor k del escalamiento")}
        </GrupoDeFila>
      </div>

      <Boton onClick={verificar} disabled={cargando}>
        {cargando ? "Verificando…" : "Verificar propiedades"}
      </Boton>

      {cargando && <Cargando texto="Calculando ambos miembros de cada propiedad…" />}
      <AvisoError error={error} />
      {resultado && <ResultadoVerificador resultado={resultado} />}
    </div>
  );
}

/** Fila de controles de una operación elemental; se resalta si el backend la rechaza. */
function GrupoDeFila({ titulo, notacion, conError, children }) {
  return (
    <div
      className={
        "flex flex-wrap items-center gap-x-6 gap-y-2 rounded-xl border px-4 py-2 " +
        (conError
          ? "border-inconsistente bg-inconsistente/5"
          : "border-[var(--borde)] bg-white")
      }
    >
      <div className="w-44">
        <p className="font-display text-sm font-bold text-tinta">{titulo}</p>
        <p className="font-mono text-xs text-grafito">{notacion}</p>
      </div>
      {children}
    </div>
  );
}

function ResultadoVerificador({ resultado }) {
  const {
    propiedades,
    operaciones_fila: operacionesFila,
    triangular,
    determinante_producto: detProducto,
    procedimientos,
  } = resultado;
  const veredictos = [
    ...propiedades.map((propiedad) => propiedad.cumple),
    operacionesFila.casos.every((caso) => caso.cumple),
    triangular.cumple,
    detProducto.cumple,
  ];
  const cumplidas = veredictos.filter(Boolean).length;
  const todas = cumplidas === veredictos.length;

  return (
    <TarjetaResultado titulo="Verificador de propiedades" formula={`A, B invertibles · n = ${resultado.n}`}>
      <div className="space-y-5">
        {propiedades.map((propiedad) => (
          <TarjetaNumerada key={propiedad.numero} numero={propiedad.numero} titulo={propiedad.enunciado}>
            {propiedad.tipo === "matriz" ? (
              <IgualdadMatricial igualdad={propiedad} />
            ) : (
              <>
                <p className="font-mono text-sm">
                  det(A) = {textoFraccion(operacionesFila.determinante)}
                </p>
                <IgualdadEscalar igualdad={propiedad} />
              </>
            )}
            <PasoAPaso claves={propiedad.pasos} procedimientos={procedimientos} />
          </TarjetaNumerada>
        ))}

        <TarjetaNumerada
          numero="5"
          titulo="Operaciones de fila y determinante"
          nota={`det(A) = ${textoFraccion(operacionesFila.determinante)}`}
        >
          {operacionesFila.casos.map((caso) => (
            <CasoDeFila key={caso.id} caso={caso} procedimientos={procedimientos} />
          ))}
        </TarjetaNumerada>

        <TarjetaNumerada numero="6" titulo="Matriz triangular: det(A) = ± producto de la diagonal">
          <ReduccionTriangular reduccion={triangular.reduccion} />
          <IgualdadEscalar igualdad={triangular} />
          <PasoAPaso claves={triangular.pasos} procedimientos={procedimientos} />
        </TarjetaNumerada>

        {/* Propiedad 7: AB, det(A), det(B) y ambos miembros llegan ya calculados del backend. */}
        <TarjetaNumerada numero="7" titulo={detProducto.enunciado}>
          <div className="flex overflow-x-auto">
            <MatrizNombrada nombre="AB" matriz={detProducto.AB} />
          </div>
          <p className="font-mono text-sm">
            det(A) = {textoFraccion(detProducto.det_A)}, det(B) = {textoFraccion(detProducto.det_B)}
          </p>
          <IgualdadEscalar igualdad={detProducto} />
          <PasoAPaso claves={detProducto.pasos} procedimientos={procedimientos} />
        </TarjetaNumerada>

        <div className={`math-solution-banner ${todas ? "math-solution-ok" : "math-solution-error"}`}>
          <div
            className="math-solution-icon"
            style={{ color: `var(--${todas ? "determinado" : "inconsistente"})` }}
          >
            {todas ? "✓" : "✗"}
          </div>
          <div>
            <p className={`font-display text-lg font-bold ${todas ? "text-determinado" : "text-inconsistente"}`}>
              Se cumplen {cumplidas} de {veredictos.length} propiedades
            </p>
            <p className="mt-1 text-sm text-tinta">
              Cada propiedad se comprobó calculando sus dos miembros por separado y
              comparándolos con fracciones exactas.
            </p>
          </div>
        </div>
      </div>
    </TarjetaResultado>
  );
}

/** Los dos miembros (matrices) de una propiedad y su veredicto. */
function IgualdadMatricial({ igualdad }) {
  const { izquierda, derecha, cumple } = igualdad;
  return (
    <>
      <div className="flex flex-wrap items-center gap-3 overflow-x-auto">
        <MatrizNombrada nombre={izquierda.nombre} matriz={izquierda.valor} />
        <Operador>{cumple ? "=" : "≠"}</Operador>
        <MatrizNombrada nombre={derecha.nombre} matriz={derecha.valor} />
      </div>
      <Veredicto cumple={cumple}>{igualdad.conclusion}</Veredicto>
    </>
  );
}

/** Una operación de fila: la matriz modificada A′ y cómo cambió el determinante. */
function CasoDeFila({ caso, procedimientos }) {
  return (
    <div className="space-y-3 border-t border-[var(--borde)] pt-4 first:border-t-0 first:pt-0">
      <div className="flex flex-wrap items-center gap-3">
        <span className="rounded bg-pivote/10 px-2 py-0.5 font-display text-sm font-semibold text-pivote">
          {caso.notacion}
        </span>
        <span className="text-sm text-grafito">{caso.efecto}</span>
      </div>
      <div className="flex overflow-x-auto">
        <MatrizNombrada nombre="A′" matriz={caso.matriz} />
      </div>
      <IgualdadEscalar igualdad={caso} />
      <PasoAPaso claves={caso.pasos} procedimientos={procedimientos} />
    </div>
  );
}

/** Botón que despliega, en orden, los cálculos que dieron los dos miembros de una propiedad. */
function PasoAPaso({ claves, procedimientos }) {
  const [visible, setVisible] = useState(false);
  return (
    <div className="space-y-4">
      <Boton
        variante="secundario"
        aria-expanded={visible}
        onClick={() => setVisible((previo) => !previo)}
      >
        {visible ? "Ocultar el paso a paso" : "Ver el paso a paso"}
      </Boton>
      {visible && (
        <ol className="space-y-4" style={{ animation: "aparecer-paso 0.3s ease both" }}>
          {claves.map((clave, indice) => (
            <Procedimiento key={clave} numero={indice + 1} procedimiento={procedimientos[clave]} />
          ))}
        </ol>
      )}
    </div>
  );
}

/** Un paso: su título y el dibujo que corresponde a su tipo de cálculo. */
function Procedimiento({ numero, procedimiento }) {
  const { tipo, titulo } = procedimiento;
  return (
    <li className="space-y-3 rounded-xl border border-[var(--borde)] bg-white p-4">
      <p className="font-display text-sm font-bold text-tinta">
        <span className="text-pivote">Paso {numero}.</span> {titulo}
      </p>
      {tipo === "inversa" && <InversaPasoAPaso procedimiento={procedimiento} />}
      {tipo === "producto" && (
        <VisualProducto factores={procedimiento.factores} resultado={procedimiento.resultado} />
      )}
      {tipo === "transpuesta" && (
        <VisualTranspuesta origen={procedimiento.origen} destino={procedimiento.destino} />
      )}
      {tipo === "det_reduccion" && (
        <ReduccionTriangular
          reduccion={procedimiento.reduccion}
          nombre={procedimiento.nombre}
          pasoAPaso
        />
      )}
      {tipo === "det_cofactores" && <ExpansionPorCofactores procedimiento={procedimiento} />}
      {tipo === "operacion_fila" && <OperacionDeFila procedimiento={procedimiento} />}
      {tipo === "cuenta" && <p className="font-mono text-sm text-tinta">{procedimiento.cuenta}</p>}
    </li>
  );
}

/** Gauss-Jordan sobre [M | I], una operación a la vez, y la inversa que queda a la derecha. */
function InversaPasoAPaso({ procedimiento }) {
  const { inversa, nombre_inversa: nombreInversa } = procedimiento;
  return (
    <>
      <ReduccionPorFilas
        matrizInicial={procedimiento.aumentada_inicial}
        pasos={procedimiento.pasos_detalle}
        columnasPivote={procedimiento.columnas_pivote}
        columnasDerecha={inversa.length}
      />
      <div className="flex overflow-x-auto">
        <MatrizNombrada nombre={nombreInversa} matriz={inversa} destacada />
      </div>
    </>
  );
}

/** det(M) por cofactores sobre la fila 1: cada menor M₁ⱼ, su determinante y su cofactor C₁ⱼ. */
function ExpansionPorCofactores({ procedimiento }) {
  const { nombre, terminos, valor } = procedimiento;
  // Una matriz 1×1 no tiene menores: su determinante es su único elemento.
  if (terminos.length === 1) {
    return (
      <p className="font-mono text-sm text-tinta">
        det({nombre}) = {textoFraccion(valor)} (matriz 1×1: su único elemento)
      </p>
    );
  }
  const suma = terminos
    .map((termino) => `(${textoFraccion(termino.entrada)})·(${textoFraccion(termino.cofactor)})`)
    .join(" + ");
  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-3">
        {terminos.map((termino, columna) => {
          const j = subindice(columna + 1);
          return (
            <div key={columna} className="space-y-2 rounded-xl border border-[var(--borde)] p-3">
              <MatrizNombrada nombre={`M₁${j}`} matriz={termino.menor} />
              <p className="font-mono text-xs text-tinta">
                C₁{j} = {termino.signo}det(M₁{j}) = {termino.signo}(
                {textoFraccion(termino.det_menor)}) ={" "}
                <span className="font-semibold text-pivote">{textoFraccion(termino.cofactor)}</span>
              </p>
            </div>
          );
        })}
      </div>
      <p className="font-mono text-sm leading-7 text-tinta">
        det({nombre}) = Σ a₁ⱼ·C₁ⱼ = {suma} = <strong>{textoFraccion(valor)}</strong>
      </p>
    </div>
  );
}

/** A antes y después de la operación de fila, con las celdas que cambian resaltadas. */
function OperacionDeFila({ procedimiento }) {
  const { notacion, antes, despues } = procedimiento;
  return (
    <div className="flex flex-wrap items-center gap-x-4 gap-y-3 overflow-x-auto">
      <MatrizNombrada nombre="A" matriz={antes} />
      <div className="flex flex-col items-center text-pivote">
        <span className="font-display text-xs font-semibold">{notacion}</span>
        <span className="text-2xl leading-none">⟶</span>
      </div>
      <MatrizNombrada
        nombre="A′"
        matriz={despues}
        celdasResaltadas={celdasCambiadas(antes, despues)}
      />
    </div>
  );
}
