// Opción 9 del Programa 5: verificador de propiedades con A y B invertibles
// del mismo orden n.
//
//   1. (A⁻¹)⁻¹ = A            4. det(A⁻¹) = 1/det(A)
//   2. (AB)⁻¹ = B⁻¹A⁻¹        5. efecto de las operaciones de fila sobre det(A)
//   3. (Aᵀ)⁻¹ = (A⁻¹)ᵀ        6. matriz triangular: det = ± producto de la diagonal
//
// El backend calcula ambos miembros de cada propiedad y decide el veredicto.

import { useState } from "react";
import { ErrorDeCalculo, programa5 } from "../../lib/api.js";
import { textoFraccion } from "../../lib/formato.js";
import Boton from "../ui/Boton.jsx";
import SelectorDimension from "../ui/SelectorDimension.jsx";
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
  const { propiedades, operaciones_fila: operacionesFila, triangular } = resultado;
  const veredictos = [
    ...propiedades.map((propiedad) => propiedad.cumple),
    operacionesFila.casos.every((caso) => caso.cumple),
    triangular.cumple,
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
          </TarjetaNumerada>
        ))}

        <TarjetaNumerada
          numero="5"
          titulo="Operaciones de fila y determinante"
          nota={`det(A) = ${textoFraccion(operacionesFila.determinante)}`}
        >
          {operacionesFila.casos.map((caso) => (
            <CasoDeFila key={caso.id} caso={caso} />
          ))}
        </TarjetaNumerada>

        <TarjetaNumerada numero="6" titulo="Matriz triangular: det(A) = ± producto de la diagonal">
          <ReduccionTriangular reduccion={triangular.reduccion} />
          <IgualdadEscalar igualdad={triangular} />
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
function CasoDeFila({ caso }) {
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
    </div>
  );
}
