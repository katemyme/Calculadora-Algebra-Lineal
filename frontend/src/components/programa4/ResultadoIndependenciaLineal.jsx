// Resultado de Vectores → Independencia Lineal: sistema homogéneo, reducción
// por filas (visual, en un toggle), matriz reducida, pivotes, variables libres
// y, al final, el veredicto teórico explícito (L.I. o L.D.).
// Solo presenta los datos que calculó el backend.

import { useState } from "react";
import { nombreVariable } from "../../lib/formato.js";
import Boton from "../ui/Boton.jsx";
import MatrizEstatica from "../MatrizEstatica.jsx";
import ReduccionPorFilas from "./ReduccionPorFilas.jsx";
import { BloqueMatriz, TarjetaResultado } from "../programa3/comunes.jsx";

function Metrica({ etiqueta, valor, resalte = false }) {
  return (
    <div className="math-value-card flex-col items-start gap-0.5">
      <span className="text-xs font-semibold uppercase tracking-wide text-grafito">
        {etiqueta}
      </span>
      <span
        className={`font-mono text-2xl font-bold nums-tabulares ${
          resalte ? "text-pivote" : "text-tinta"
        }`}
      >
        {valor}
      </span>
    </div>
  );
}

const listaVariables = (columnas) =>
  columnas.map((j) => nombreVariable(j, "c")).join(", ");

export default function ResultadoIndependenciaLineal({ resultado }) {
  const [verTeoremas, setVerTeoremas] = useState(false);
  const [verReduccion, setVerReduccion] = useState(false);
  const {
    k,
    n,
    independientes,
    pivotes,
    variables_libres: libres,
    columnas_pivote: columnasPivote,
    columnas_libres: columnasLibres,
  } = resultado;

  return (
    <TarjetaResultado titulo="Independencia lineal" formula="Ax = 0">
      <div className="space-y-6">
        <div className="grid gap-3 sm:grid-cols-2">
          <Metrica etiqueta="Vectores k" valor={k} />
          <Metrica etiqueta="Dimensión n" valor={n} />
        </div>

        {/* Matrices: sistema homogéneo → reducción por filas → matriz reducida */}
        <div className="space-y-5">
          <div className="space-y-2 overflow-x-auto">
            <p className="text-sm font-semibold text-grafito">
              Sistema homogéneo [A | 0]
            </p>
            <BloqueMatriz orden={`${n} × ${k + 1}`}>
              <MatrizEstatica matriz={resultado.matriz_inicial} />
            </BloqueMatriz>
          </div>

          <div className="math-info-card space-y-4">
            <Boton
              variante="secundario"
              aria-expanded={verReduccion}
              onClick={() => setVerReduccion((previo) => !previo)}
            >
              {verReduccion
                ? "Ocultar reducción por filas"
                : `Ver reducción por filas (${resultado.pasos_detalle.length} operaciones)`}
            </Boton>
            {verReduccion && (
              <div style={{ animation: "aparecer-paso 0.3s ease both" }}>
                <ReduccionPorFilas
                  matrizInicial={resultado.matriz_inicial}
                  pasos={resultado.pasos_detalle}
                  columnasPivote={columnasPivote}
                />
              </div>
            )}
          </div>

          <div className="space-y-2 overflow-x-auto">
            <p className="text-sm font-semibold text-grafito">
              Matriz reducida (forma escalonada reducida)
            </p>
            <BloqueMatriz orden={`${n} × ${k + 1}`}>
              <MatrizEstatica
                matriz={resultado.matriz_reducida}
                columnasPivote={columnasPivote}
              />
            </BloqueMatriz>
          </div>
        </div>

        <div className="grid gap-3 md:grid-cols-2">
          <div className="math-info-card">
            <p className="text-xs font-semibold uppercase tracking-wide text-grafito">
              Columnas pivote (variables básicas)
            </p>
            <p className="mt-1 font-mono text-tinta">
              {columnasPivote.length ? listaVariables(columnasPivote) : "ninguna"}
            </p>
          </div>
          <div className="math-info-card">
            <p className="text-xs font-semibold uppercase tracking-wide text-grafito">
              Variables libres
            </p>
            <p className="mt-1 font-mono text-tinta">
              {columnasLibres.length ? listaVariables(columnasLibres) : "ninguna"}
            </p>
          </div>
        </div>

        {/* Veredicto teórico */}
        <div
          className={`math-solution-banner ${
            independientes ? "math-solution-ok" : "math-solution-error"
          }`}
        >
          <div
            className="math-solution-icon"
            style={{ color: `var(--${independientes ? "determinado" : "inconsistente"})` }}
          >
            {independientes ? "⊥" : "∥"}
          </div>
          <div>
            <p
              className={`font-display text-xl font-bold ${
                independientes ? "text-determinado" : "text-inconsistente"
              }`}
            >
              Veredicto:{" "}
              {independientes
                ? "Linealmente Independiente (L.I.)"
                : "Linealmente Dependiente (L.D.)"}
            </p>
            <p className="mt-1 text-sm text-tinta">
              {independientes ? (
                <>
                  Hay {pivotes} pivotes = k = {k} vectores: no hay variables libres, así
                  que la única solución de Ax = 0 es la trivial c₁ = … = cₖ = 0.
                </>
              ) : (
                <>
                  Hay {pivotes} pivote(s) &lt; k = {k} vectores: queda(n) {libres}{" "}
                  variable(s) libre(s) ({listaVariables(columnasLibres)}), por lo que Ax
                  = 0 tiene soluciones no triviales.
                </>
              )}
            </p>
          </div>
        </div>

        {/* Teoremas: solo se muestran al pedirlos, al final del flujo */}
        <div className="space-y-3">
          <Boton
            variante="secundario"
            aria-expanded={verTeoremas}
            onClick={() => setVerTeoremas((previo) => !previo)}
          >
            {verTeoremas
              ? "Ocultar teoremas clave del módulo"
              : "Ver teoremas clave del módulo"}
          </Boton>
          {verTeoremas && (
            <div
              className="math-info-card"
              style={{ animation: "aparecer-paso 0.3s ease both" }}
            >
              <p className="text-xs font-semibold uppercase tracking-wide text-grafito">
                Teoremas clave del módulo
              </p>
              <p className="mt-1 text-sm leading-6 text-tinta">{resultado.teorema}</p>
            </div>
          )}
        </div>
      </div>
    </TarjetaResultado>
  );
}
